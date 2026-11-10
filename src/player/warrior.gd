extends CharacterBody3D

signal health_changed(current, max_val)
signal stamina_changed(current, max_val)
signal died

enum State { IDLE, RUN, ATTACK, DODGE, PRAY, HIT, DEAD }

@export var base_speed: float = 7.0
@export var dodge_speed: float = 14.0
@export var gravity: float = 24.0

var max_health: float = 120.0
var current_health: float = 120.0
var max_stamina: float = 100.0
var current_stamina: float = 100.0
var stamina_regen: float = 35.0

var current_state: State = State.IDLE
var attack_combo: int = 0
var combo_window_open: bool = false
var is_invulnerable: bool = false
var is_dead: bool = false
var ares_buff_timer: float = 0.0

@onready var anim_player: AnimationPlayer = $Model/AnimationPlayer
@onready var camera_pivot = get_parent().get_node_or_null("CameraPivot")
@onready var ares_aura = $AresAura
@onready var hit_spark = $HitSpark

func _ready():
	add_to_group("player")
	if ares_aura:
		ares_aura.visible = false
	emit_signal("health_changed", current_health, max_health)
	emit_signal("stamina_changed", current_stamina, max_stamina)
	_play_anim("Idle")

func _process(delta):
	if is_dead:
		return

	# Stamina regeneration
	if current_state != State.DODGE and current_state != State.ATTACK:
		current_stamina = min(max_stamina, current_stamina + stamina_regen * delta)
		emit_signal("stamina_changed", current_stamina, max_stamina)

	# Ares buff decay
	if ares_buff_timer > 0.0:
		ares_buff_timer -= delta
		if ares_buff_timer <= 0.0 and ares_aura:
			ares_aura.visible = false

	# Divine power inputs
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

	# Apply gravity
	if not is_on_floor():
		velocity.y -= gravity * delta

	match current_state:
		State.IDLE, State.RUN:
			_handle_movement(delta)
			if Input.is_action_just_pressed("attack"):
				_start_attack(1)
			elif Input.is_action_just_pressed("dodge") and current_stamina >= 25.0:
				_start_dodge()

		State.ATTACK:
			# Slow deceleration during swing
			velocity.x = move_toward(velocity.x, 0, 18.0 * delta)
			velocity.z = move_toward(velocity.z, 0, 18.0 * delta)
			move_and_slide()
			if combo_window_open and Input.is_action_just_pressed("attack"):
				if attack_combo == 1:
					_start_attack(2)

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

	if move_dir.length_squared() > 0.01:
		velocity.x = move_dir.x * current_speed
		velocity.z = move_dir.z * current_speed

		# Smooth character rotation towards movement
		var target_angle = atan2(move_dir.x, move_dir.z)
		rotation.y = lerp_angle(rotation.y, target_angle, 14.0 * delta)

		if current_state != State.RUN:
			current_state = State.RUN
			_play_anim("Run")
	else:
		velocity.x = move_toward(velocity.x, 0, current_speed * 12.0 * delta)
		velocity.z = move_toward(velocity.z, 0, current_speed * 12.0 * delta)
		if current_state != State.IDLE:
			current_state = State.IDLE
			_play_anim("Idle")

	move_and_slide()

func _start_attack(combo_step: int):
	if current_stamina < 15.0:
		return

	current_stamina -= 15.0
	emit_signal("stamina_changed", current_stamina, max_stamina)
	current_state = State.ATTACK
	attack_combo = combo_step
	combo_window_open = false

	# Slight step forward during attack
	var forward = -transform.basis.z
	velocity.x = forward.x * 4.5
	velocity.z = forward.z * 4.5

	SoundManager.play("sword_swing", 1.0 + (0.15 * combo_step))
	_play_anim("Attack" + str(combo_step))

	# Schedule hit impact check and combo window
	get_tree().create_timer(0.18).timeout.connect(func(): _execute_melee_hit(combo_step))
	get_tree().create_timer(0.25).timeout.connect(func(): combo_window_open = true)
	get_tree().create_timer(0.55).timeout.connect(_finish_attack)

func _execute_melee_hit(combo_step: int):
	if current_state != State.ATTACK or is_dead:
		return

	var base_dmg = 40.0 if combo_step == 1 else 65.0
	var final_dmg = base_dmg * (2.2 if ares_buff_timer > 0.0 else 1.0)
	var forward = -transform.basis.z
	var hit_center = global_position + forward * 1.6 + Vector3.UP * 0.8
	var hit_radius = 2.4

	var enemies = get_tree().get_nodes_in_group("enemies")
	var hit_any = false

	for enemy in enemies:
		if is_instance_valid(enemy):
			var dist = hit_center.distance_to(enemy.global_position)
			if dist <= hit_radius:
				hit_any = true
				var knockback = forward * (12.0 if combo_step == 1 else 20.0) + Vector3.UP * 3.0
				enemy.take_damage(final_dmg, knockback, "melee")

	if hit_any:
		SoundManager.play("sword_hit", 1.0)
		if combo_step == 2 and randf() < 0.5:
			SoundManager.play_dialogue("warrior_attack")
		if hit_spark:
			hit_spark.restart()

func _finish_attack():
	if current_state == State.ATTACK and not is_dead:
		combo_window_open = false
		attack_combo = 0
		current_state = State.IDLE
		_play_anim("Idle")

func _start_dodge():
	current_stamina -= 25.0
	emit_signal("stamina_changed", current_stamina, max_stamina)
	current_state = State.DODGE
	is_invulnerable = true

	# Dodge in current input direction, or backward/forward if stationary
	var forward = -transform.basis.z
	velocity.x = forward.x * dodge_speed
	velocity.z = forward.z * dodge_speed

	_play_anim("Dodge")
	SoundManager.play("sword_swing", 0.8)

	get_tree().create_timer(0.38).timeout.connect(func(): is_invulnerable = false)
	get_tree().create_timer(0.55).timeout.connect(_finish_dodge)

func _finish_dodge():
	if current_state == State.DODGE and not is_dead:
		is_invulnerable = false
		current_state = State.IDLE
		_play_anim("Idle")

func start_praying(god_name: String):
	if current_state != State.PRAY and not is_dead:
		current_state = State.PRAY
		_play_anim("Pray")

func stop_praying():
	if current_state == State.PRAY and not is_dead:
		current_state = State.IDLE
		_play_anim("Idle")

func _try_cast(god: String):
	if is_dead or current_state == State.DEAD:
		return
	var forward = -transform.basis.z
	DivineManager.cast_power(god, global_position, forward)

func activate_ares_buff(duration: float):
	ares_buff_timer = duration
	if ares_aura:
		ares_aura.visible = true

func heal(amount: float):
	if is_dead:
		return
	current_health = min(max_health, current_health + amount)
	emit_signal("health_changed", current_health, max_health)

func take_damage(amount: float, knockback: Vector3 = Vector3.ZERO):
	if is_invulnerable or is_dead:
		return

	current_health = max(0.0, current_health - amount)
	emit_signal("health_changed", current_health, max_health)
	SoundManager.play("player_hurt", 1.0)
	if randf() < 0.45:
		SoundManager.play_dialogue("warrior_hurt")

	if current_health <= 0.0:
		_die()
	else:
		velocity += knockback * 0.5
		if current_state != State.ATTACK:
			current_state = State.HIT
			_play_anim("Hit")
			get_tree().create_timer(0.3).timeout.connect(func():
				if current_state == State.HIT and not is_dead:
					current_state = State.IDLE
					_play_anim("Idle")
			)

func _die():
	is_dead = true
	current_state = State.DEAD
	velocity = Vector3.ZERO
	_play_anim("Death")
	emit_signal("died")

func _play_anim(anim_name: String):
	if anim_player and anim_player.has_animation(anim_name):
		anim_player.play(anim_name)
