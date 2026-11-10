extends CharacterBody3D

signal health_changed(current, max_val)
signal stamina_changed(current, max_val)
signal died

enum State { IDLE, RUN, AIM, ATTACK, DODGE, PRAY, HIT, DEAD }

@export var base_speed: float = 8.5
@export var dodge_speed: float = 15.0
@export var gravity: float = 24.0

var max_health: float = 100.0
var current_health: float = 100.0
var max_stamina: float = 100.0
var current_stamina: float = 100.0
var stamina_regen: float = 40.0

var current_state: State = State.IDLE
var is_invulnerable: bool = false
var is_dead: bool = false
var ares_buff_timer: float = 0.0
var shoot_cooldown: float = 0.0

var arrow_scene = preload("res://src/player/arrow.tscn")

@onready var anim_player: AnimationPlayer = $Model/AnimationPlayer
@onready var camera_pivot = get_parent().get_node_or_null("CameraPivot")
@onready var ares_aura = $AresAura
@onready var bow_tip = $BowTip

func _ready():
	add_to_group("player")
	if ares_aura:
		ares_aura.visible = false
	emit_signal("health_changed", current_health, max_health)
	emit_signal("stamina_changed", current_stamina, max_stamina)
	_play_anim("Idle")
	SoundManager.play_dialogue("archer_select")

func _process(delta):
	if is_dead:
		return

	if shoot_cooldown > 0.0:
		shoot_cooldown -= delta

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
			if Input.is_action_pressed("attack") and shoot_cooldown <= 0.0 and current_stamina >= 10.0:
				_shoot_arrow()
			elif Input.is_action_just_pressed("dodge") and current_stamina >= 20.0:
				_start_dodge()

		State.ATTACK:
			velocity.x = move_toward(velocity.x, 0, 16.0 * delta)
			velocity.z = move_toward(velocity.z, 0, 16.0 * delta)
			move_and_slide()

		State.DODGE:
			move_and_slide()

		State.PRAY:
			velocity.x = 0
			velocity.z = 0
			move_and_slide()

		State.HIT:
			velocity.x = move_toward(velocity.x, 0, 20.0 * delta)
			velocity.z = move_toward(velocity.z, 0, 20.0 * delta)
			move_and_slide()

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
	var current_speed = base_speed * (1.35 if ares_buff_timer > 0.0 else 1.0)

	if move_dir.length() > 0.1:
		velocity.x = move_dir.x * current_speed
		velocity.z = move_dir.z * current_speed
		var target_rot = atan2(-move_dir.x, -move_dir.z)
		rotation.y = lerp_angle(rotation.y, target_rot, 12.0 * delta)
		if current_state == State.IDLE:
			current_state = State.RUN
			_play_anim("Run")
	else:
		velocity.x = move_toward(velocity.x, 0, 22.0 * delta)
		velocity.z = move_toward(velocity.z, 0, 22.0 * delta)
		if current_state == State.RUN:
			current_state = State.IDLE
			_play_anim("Idle")

	move_and_slide()

func _shoot_arrow(is_fire: bool = false):
	current_state = State.ATTACK
	shoot_cooldown = 0.40
	current_stamina -= 12.0
	emit_signal("stamina_changed", current_stamina, max_stamina)
	_play_anim("Attack")

	# Orient character towards camera facing
	if camera_pivot and camera_pivot.has_method("get_camera_basis"):
		var cam_forward = -camera_pivot.get_camera_basis().z
		cam_forward.y = 0
		if cam_forward.length() > 0.1:
			rotation.y = atan2(-cam_forward.x, -cam_forward.z)

	var spawn_pos = global_position + Vector3(0, 1.4, 0)
	var shoot_dir = -global_transform.basis.z

	var arrow = arrow_scene.instantiate()
	arrow.global_position = spawn_pos
	arrow.direction = shoot_dir.normalized()
	arrow.is_enemy_arrow = false
	arrow.is_fire_arrow = is_fire or (ares_buff_timer > 0.0)
	get_parent().add_child(arrow)

	SoundManager.play("arrow_shoot", randf_range(0.95, 1.05))
	if randf() < 0.2:
		SoundManager.play_dialogue("archer_shoot")

	await get_tree().create_timer(0.35).timeout
	if current_state == State.ATTACK:
		current_state = State.IDLE
		_play_anim("Idle")

func _start_dodge():
	current_state = State.DODGE
	is_invulnerable = true
	current_stamina -= 20.0
	emit_signal("stamina_changed", current_stamina, max_stamina)

	var dodge_dir = -global_transform.basis.z
	velocity = dodge_dir * dodge_speed
	_play_anim("Dodge")

	await get_tree().create_timer(0.35).timeout
	is_invulnerable = false
	if current_state == State.DODGE:
		current_state = State.IDLE
		_play_anim("Idle")

func take_damage(amount: float, attacker_pos: Vector3 = Vector3.ZERO):
	if is_invulnerable or is_dead:
		return
	current_health = max(0.0, current_health - amount)
	emit_signal("health_changed", current_health, max_health)
	SoundManager.play("player_hurt", randf_range(0.9, 1.1))

	if attacker_pos != Vector3.ZERO:
		var knock_dir = (global_position - attacker_pos).normalized()
		knock_dir.y = 0
		velocity = knock_dir * 8.0

	if current_health <= 0.0:
		_die()
	else:
		current_state = State.HIT
		_play_anim("Hit")
		await get_tree().create_timer(0.25).timeout
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
		DivineManager.cast_power(god_id, self)
		if god_id == "ares":
			ares_buff_timer = 8.0
			if ares_aura:
				ares_aura.visible = true

func _play_anim(anim_name: String):
	if anim_player and anim_player.has_animation(anim_name):
		anim_player.play(anim_name)
