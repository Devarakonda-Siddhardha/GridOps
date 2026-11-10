extends CharacterBody3D

signal health_changed(current, max_val)
signal stamina_changed(current, max_val)
signal died

enum State { IDLE, RUN, ATTACK, DODGE, PRAY, HIT, DEAD }

@export var base_speed: float = 12.0
@export var sprint_speed: float = 16.5
@export var jump_velocity: float = 10.0
@export var gravity: float = 24.0

var max_health: float = 160.0
var current_health: float = 160.0
var max_stamina: float = 120.0
var current_stamina: float = 120.0
var stamina_regen: float = 30.0

var current_state: State = State.IDLE
var is_invulnerable: bool = false
var is_dead: bool = false
var ares_buff_timer: float = 0.0
var trample_cooldown: float = 0.0
var gallop_sound_timer: float = 0.0

@onready var anim_player: AnimationPlayer = $Model/AnimationPlayer
@onready var camera_pivot = get_parent().get_node_or_null("CameraPivot")
@onready var ares_aura = $AresAura
@onready var hit_spark = $HitSpark

func _ready():
	add_to_group("player")
	floor_max_angle = deg_to_rad(60.0)
	floor_snap_length = 0.35
	floor_constant_speed = true
	floor_stop_on_slope = true
	if ares_aura:
		ares_aura.visible = false
	emit_signal("health_changed", current_health, max_health)
	emit_signal("stamina_changed", current_stamina, max_stamina)
	_play_anim("Idle")
	SoundManager.play_dialogue("cavalry_select")
	SoundManager.play("horse_neigh", 1.0)

func _process(delta):
	if is_dead:
		return

	if trample_cooldown > 0.0:
		trample_cooldown -= delta

	if current_state != State.DODGE and current_state != State.ATTACK:
		current_stamina = min(max_stamina, current_stamina + stamina_regen * delta)
		emit_signal("stamina_changed", current_stamina, max_stamina)

	if ares_buff_timer > 0.0:
		ares_buff_timer -= delta
		if ares_buff_timer <= 0.0 and ares_aura:
			ares_aura.visible = false

	# Divine powers
	if Input.is_action_just_pressed("power_zeus"):
		_try_cast("zeus")
	elif Input.is_action_just_pressed("power_poseidon"):
		_try_cast("poseidon")
	elif Input.is_action_just_pressed("power_hades"):
		_try_cast("hades")
	elif Input.is_action_just_pressed("power_ares"):
		_try_cast("ares")

func _physics_process(delta):
	if is_dead:
		return

	if not is_on_floor():
		velocity.y -= gravity * delta

	match current_state:
		State.IDLE, State.RUN:
			_handle_movement(delta)
			if is_on_floor() and Input.is_action_just_pressed("jump"):
				_horse_leap()
			elif Input.is_action_just_pressed("attack") and current_stamina >= 15.0:
				_lance_thrust()
			elif Input.is_action_just_pressed("dodge") and current_stamina >= 25.0:
				_horse_dash()

		State.ATTACK:
			velocity.x = move_toward(velocity.x, 0, 10.0 * delta)
			velocity.z = move_toward(velocity.z, 0, 10.0 * delta)
			move_and_slide()

		State.DODGE:
			move_and_slide()

		State.PRAY:
			velocity.x = 0
			velocity.z = 0
			move_and_slide()

		State.HIT:
			velocity.x = move_toward(velocity.x, 0, 16.0 * delta)
			velocity.z = move_toward(velocity.z, 0, 16.0 * delta)
			move_and_slide()

	# Trample mechanic during gallop
	if current_state == State.RUN and velocity.length() > 8.0 and trample_cooldown <= 0.0:
		_check_trample()

func _handle_movement(delta):
	var input_dir = Vector2.ZERO
	if Input.is_action_pressed("move_forward"):
		input_dir.y -= 1
	if Input.is_action_pressed("move_backward"):
		input_dir.y += 1
	if Input.is_action_pressed("move_left"):
		input_dir.x -= 1
	if Input.is_action_pressed("move_right"):
		input_dir.x += 1
	input_dir = input_dir.normalized()

	var cam_basis = Basis.IDENTITY
	if camera_pivot and camera_pivot.has_method("get_camera_basis"):
		cam_basis = camera_pivot.get_camera_basis()

	var move_dir = (cam_basis * Vector3(input_dir.x, 0, input_dir.y)).normalized()
	var current_speed = sprint_speed if ares_buff_timer > 0.0 else base_speed

	if move_dir.length() > 0.1:
		velocity.x = move_dir.x * current_speed
		velocity.z = move_dir.z * current_speed
		var target_rot = atan2(-move_dir.x, -move_dir.z)
		rotation.y = lerp_angle(rotation.y, target_rot, 10.0 * delta)
		if current_state == State.IDLE:
			current_state = State.RUN
			_play_anim("Run")

		# Rhythmic hoof beats
		gallop_sound_timer -= delta
		if gallop_sound_timer <= 0.0:
			gallop_sound_timer = 0.35
			SoundManager.play("horse_gallop", randf_range(0.9, 1.1), -4.0)
	else:
		velocity.x = move_toward(velocity.x, 0, 18.0 * delta)
		velocity.z = move_toward(velocity.z, 0, 18.0 * delta)
		if current_state == State.RUN:
			current_state = State.IDLE
			_play_anim("Idle")

	move_and_slide()

func _check_trample():
	var space_state = get_world_3d().direct_space_state
	var query = PhysicsShapeQueryParameters3D.new()
	var sphere = SphereShape3D.new()
	sphere.radius = 1.8
	query.shape = sphere
	query.transform = Transform3D(Basis.IDENTITY, global_position + Vector3(0, 0.8, 0))
	query.collision_mask = 2 # Enemies

	var hits = space_state.intersect_shape(query, 8)
	var trampled_any = false
	for h in hits:
		var col = h.collider
		if col and col.is_in_group("enemies") and col.has_method("take_damage"):
			var dmg = 25.0 * (2.0 if ares_buff_timer > 0.0 else 1.0)
			col.take_damage(dmg, global_position)
			trampled_any = true

	if trampled_any:
		trample_cooldown = 0.4
		SoundManager.play("lance_pierce", 0.9)
		if hit_spark:
			hit_spark.emitting = true

func _lance_thrust():
	current_state = State.ATTACK
	current_stamina -= 18.0
	emit_signal("stamina_changed", current_stamina, max_stamina)
	_play_anim("Attack")

	# Lunge forward slightly
	var thrust_dir = -global_transform.basis.z
	velocity = thrust_dir * 10.0

	SoundManager.play("lance_pierce", randf_range(0.95, 1.05))
	if randf() < 0.25:
		SoundManager.play_dialogue("cavalry_charge")

	# Hit detection with 3.2m reach
	await get_tree().create_timer(0.2).timeout
	var space_state = get_world_3d().direct_space_state
	var query = PhysicsShapeQueryParameters3D.new()
	var sphere = SphereShape3D.new()
	sphere.radius = 2.2
	query.shape = sphere
	query.transform = Transform3D(Basis.IDENTITY, global_position + thrust_dir * 2.2 + Vector3(0, 1.0, 0))
	query.collision_mask = 2 | 4

	var hits = space_state.intersect_shape(query, 12)
	var dmg = 45.0 * (2.2 if ares_buff_timer > 0.0 else 1.0)
	for h in hits:
		var col = h.collider
		if col and col.has_method("take_damage"):
			col.take_damage(dmg, global_position)

	await get_tree().create_timer(0.35).timeout
	if current_state == State.ATTACK:
		current_state = State.IDLE
		_play_anim("Idle")

func _horse_leap():
	velocity.y = jump_velocity
	SoundManager.play("horse_neigh", 1.25, -2.0)

func _get_move_direction() -> Vector3:
	var input_dir = Vector2.ZERO
	if Input.is_action_pressed("move_forward"):
		input_dir.y -= 1
	if Input.is_action_pressed("move_backward"):
		input_dir.y += 1
	if Input.is_action_pressed("move_left"):
		input_dir.x -= 1
	if Input.is_action_pressed("move_right"):
		input_dir.x += 1
	input_dir = input_dir.normalized()
	if input_dir.length_squared() < 0.01:
		return -transform.basis.z
	var cam_basis = Basis.IDENTITY
	if camera_pivot and camera_pivot.has_method("get_camera_basis"):
		cam_basis = camera_pivot.get_camera_basis()
	return (cam_basis * Vector3(input_dir.x, 0, input_dir.y)).normalized()

func _horse_dash():
	current_state = State.DODGE
	is_invulnerable = true
	current_stamina -= 25.0
	emit_signal("stamina_changed", current_stamina, max_stamina)

	var dash_dir = _get_move_direction()
	rotation.y = atan2(-dash_dir.x, -dash_dir.z)
	velocity = dash_dir * 22.0
	SoundManager.play("horse_neigh", 1.1)

	await get_tree().create_timer(0.4).timeout
	is_invulnerable = false
	if current_state == State.DODGE:
		current_state = State.IDLE
		_play_anim("Idle")

func take_damage(amount: float, attacker_pos: Vector3 = Vector3.ZERO):
	if is_invulnerable or is_dead:
		return
	current_health = max(0.0, current_health - amount)
	emit_signal("health_changed", current_health, max_health)
	SoundManager.play("player_hurt", randf_range(0.85, 0.95))

	if current_health <= 0.0:
		_die()
	else:
		current_state = State.HIT
		_play_anim("Hit")
		await get_tree().create_timer(0.3).timeout
		if current_state == State.HIT:
			current_state = State.IDLE
			_play_anim("Idle")

func heal(amount: float):
	current_health = min(max_health, current_health + amount)
	emit_signal("health_changed", current_health, max_health)

func _die():
	is_dead = true
	current_state = State.DEAD
	_play_anim("Death")
	SoundManager.play("horse_neigh", 0.7)
	emit_signal("died")

func pray_at_altar(altar_pos: Vector3):
	current_state = State.PRAY
	var dir = (altar_pos - global_position).normalized()
	rotation.y = atan2(-dir.x, -dir.z)
	_play_anim("Idle")

func finish_prayer():
	if current_state == State.PRAY:
		current_state = State.IDLE
		_play_anim("Idle")

func _try_cast(god_id: String):
	if DivineManager.can_cast(god_id):
		var forward = -global_transform.basis.z
		DivineManager.cast_power(god_id, global_position, forward)
		if god_id == "ares":
			ares_buff_timer = 8.0
			if ares_aura:
				ares_aura.visible = true

func _play_anim(anim_name: String):
	if anim_player and anim_player.has_animation(anim_name):
		anim_player.play(anim_name)
