extends CharacterBody3D

signal health_changed(current, max_val)
signal stamina_changed(current, max_val)
signal died

enum State { IDLE, RUN, ATTACK, BLOCK, DODGE, PRAY, HIT, DEAD }

@export var base_speed: float = 7.0
@export var dodge_speed: float = 14.0
@export var jump_velocity: float = 9.0
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
var action_id: int = 0

@onready var anim_player: AnimationPlayer = $Model/AnimationPlayer
@onready var model_node: Node3D = $Model
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
	_configure_loop_anims()
	emit_signal("health_changed", current_health, max_health)
	emit_signal("stamina_changed", current_stamina, max_stamina)
	_play_anim("Idle")

func _configure_loop_anims():
	if not anim_player:
		return
	for anim_name in ["Idle", "Run"]:
		if anim_player.has_animation(anim_name):
			var anim = anim_player.get_animation(anim_name)
			if anim:
				anim.loop_mode = Animation.LOOP_LINEAR

func _process(delta):
	if is_dead:
		return

	# Stamina regeneration (slower while blocking)
	if current_state != State.DODGE and current_state != State.ATTACK:
		var regen_mult = 0.35 if current_state == State.BLOCK else 1.0
		current_stamina = min(max_stamina, current_stamina + stamina_regen * regen_mult * delta)
		emit_signal("stamina_changed", current_stamina, max_stamina)

	# Smoothly tilt model into guard stance when blocking
	if model_node:
		var target_rot_y = 0.45 if current_state == State.BLOCK else 0.0
		var target_rot_x = 0.08 if current_state == State.BLOCK else 0.0
		model_node.rotation.y = lerp_angle(model_node.rotation.y, target_rot_y, 14.0 * delta)
		model_node.rotation.x = lerp(model_node.rotation.x, target_rot_x, 14.0 * delta)

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
			_handle_movement(delta, 1.0)
			if Input.is_action_pressed("block"):
				_enter_block()
			elif is_on_floor() and Input.is_action_just_pressed("jump"):
				_jump()
			elif Input.is_action_just_pressed("attack"):
				_start_attack(1)
			elif Input.is_action_just_pressed("dodge") and current_stamina >= 25.0:
				_start_dodge()

		State.BLOCK:
			_handle_movement(delta, 0.45)
			if not Input.is_action_pressed("block"):
				current_state = State.IDLE
				_play_anim("Idle")
			elif Input.is_action_just_pressed("attack"):
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
			elif combo_window_open and Input.is_action_pressed("block"):
				_enter_block()

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

func _jump():
	velocity.y = jump_velocity
	SoundManager.play("sword_swing", 1.3, -4.0)

func _enter_block():
	action_id += 1
	current_state = State.BLOCK
	combo_window_open = false
	attack_combo = 0
	if anim_player and anim_player.has_animation("ShieldBlock"):
		_play_anim("ShieldBlock")
	else:
		_play_anim("Idle")
	SoundManager.play("shield_block", 1.2, -6.0)

func _handle_movement(delta, speed_mult: float = 1.0):
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
	var current_speed = base_speed * (1.25 if ares_buff_timer > 0.0 else 1.0) * speed_mult

	if current_state == State.BLOCK:
		# Face camera forward while blocking
		var cam_forward = (cam_basis * Vector3(0, 0, -1)).normalized()
		var guard_angle = atan2(-cam_forward.x, -cam_forward.z)
		rotation.y = lerp_angle(rotation.y, guard_angle, 14.0 * delta)

	if move_dir.length() > 0.1:
		velocity.x = move_dir.x * current_speed
		velocity.z = move_dir.z * current_speed

		if current_state != State.BLOCK:
			# Smooth character rotation towards movement (facing forward)
			var target_angle = atan2(-move_dir.x, -move_dir.z)
			rotation.y = lerp_angle(rotation.y, target_angle, 14.0 * delta)

			if not is_on_floor():
				_play_anim("Idle", 0.2)
			elif current_state != State.RUN:
				current_state = State.RUN
				_play_anim("Run", 0.14)
	else:
		velocity.x = move_toward(velocity.x, 0, current_speed * 12.0 * delta)
		velocity.z = move_toward(velocity.z, 0, current_speed * 12.0 * delta)
		if current_state != State.BLOCK:
			if current_state != State.IDLE:
				current_state = State.IDLE
				_play_anim("Idle", 0.14)

	move_and_slide()

func _start_attack(combo_step: int):
	if current_stamina < 15.0:
		return

	action_id += 1
	var my_id = action_id

	current_stamina -= 15.0
	emit_signal("stamina_changed", current_stamina, max_stamina)
	current_state = State.ATTACK
	attack_combo = combo_step
	combo_window_open = false

	# Face camera forward when attacking
	if camera_pivot and camera_pivot.has_method("get_camera_basis"):
		var cam_forward = (camera_pivot.get_camera_basis() * Vector3(0, 0, -1)).normalized()
		rotation.y = atan2(-cam_forward.x, -cam_forward.z)

	# Slight step forward during attack
	var forward = -transform.basis.z
	velocity.x = forward.x * 4.5
	velocity.z = forward.z * 4.5

	SoundManager.play("sword_swing", 1.0 + (0.15 * combo_step))
	_play_anim("Attack" + str(combo_step), 0.08, true)

	# Schedule hit impact check and combo window with action_id guard
	get_tree().create_timer(0.18).timeout.connect(func():
		if is_instance_valid(self) and my_id == action_id:
			_execute_melee_hit(combo_step)
	)
	get_tree().create_timer(0.25).timeout.connect(func():
		if is_instance_valid(self) and my_id == action_id:
			combo_window_open = true
	)
	get_tree().create_timer(0.55).timeout.connect(func():
		if is_instance_valid(self) and my_id == action_id:
			_finish_attack()
	)

func _execute_melee_hit(combo_step: int):
	if current_state != State.ATTACK or is_dead:
		return

	var base_dmg = 40.0 if combo_step == 1 else 65.0
	var final_dmg = base_dmg * (2.2 if ares_buff_timer > 0.0 else 1.0)
	var forward = -transform.basis.z
	var hit_center = global_position + forward * 1.6 + Vector3.UP * 0.8
	var hit_radius = 2.4

	var targets = []
	targets.append_array(get_tree().get_nodes_in_group("enemies"))
	targets.append_array(get_tree().get_nodes_in_group("destructible"))
	var hit_any = false

	for target in targets:
		if is_instance_valid(target):
			var dist = hit_center.distance_to(target.global_position)
			var max_range = hit_radius + (1.2 if target.is_in_group("destructible") else 0.0)
			if dist <= max_range:
				hit_any = true
				var knockback = forward * (12.0 if combo_step == 1 else 20.0) + Vector3.UP * 3.0
				target.take_damage(final_dmg, knockback, "melee")

	if hit_any:
		SoundManager.play("sword_hit", 1.0)
		if combo_step == 2:
			if randf() < 0.5:
				SoundManager.play_dialogue("warrior_attack")
			AthenaCommentary.trigger_combo_praise()
		if hit_spark:
			hit_spark.restart()

func _finish_attack():
	if current_state == State.ATTACK and not is_dead:
		combo_window_open = false
		attack_combo = 0
		current_state = State.IDLE
		_play_anim("Idle", 0.14)

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

func _start_dodge():
	action_id += 1
	var my_id = action_id

	current_stamina -= 25.0
	emit_signal("stamina_changed", current_stamina, max_stamina)
	current_state = State.DODGE
	is_invulnerable = true

	var dodge_dir = _get_move_direction()
	rotation.y = atan2(-dodge_dir.x, -dodge_dir.z)
	velocity.x = dodge_dir.x * dodge_speed
	velocity.z = dodge_dir.z * dodge_speed

	_play_anim("Dodge", 0.08, true)
	SoundManager.play("sword_swing", 0.8)

	get_tree().create_timer(0.38).timeout.connect(func():
		if is_instance_valid(self) and my_id == action_id:
			is_invulnerable = false
	)
	get_tree().create_timer(0.55).timeout.connect(func():
		if is_instance_valid(self) and my_id == action_id:
			_finish_dodge()
	)

func _finish_dodge():
	if current_state == State.DODGE and not is_dead:
		is_invulnerable = false
		current_state = State.IDLE
		_play_anim("Idle", 0.14)

func start_praying(_god_name: String):
	if current_state != State.PRAY and not is_dead:
		action_id += 1
		current_state = State.PRAY
		_play_anim("Pray", 0.14)

func stop_praying():
	if current_state == State.PRAY and not is_dead:
		current_state = State.IDLE
		_play_anim("Idle", 0.14)

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

	# Shield Block check (Right-Click)
	if current_state == State.BLOCK:
		if current_stamina >= 10.0:
			current_stamina -= 10.0
			emit_signal("stamina_changed", current_stamina, max_stamina)
			SoundManager.play("shield_block", randf_range(0.95, 1.05))
			AthenaCommentary.trigger_block_praise()
			if hit_spark:
				hit_spark.restart()
			velocity += knockback * 0.25
			return
		else:
			# Guard broken / low stamina: 70% damage reduction
			amount *= 0.3

	current_health = max(0.0, current_health - amount)
	emit_signal("health_changed", current_health, max_health)
	SoundManager.play("player_hurt", 1.0)
	if randf() < 0.45:
		SoundManager.play_dialogue("warrior_hurt")

	if current_health <= 0.0:
		_die()
	else:
		velocity += knockback * 0.5
		if current_state != State.ATTACK and current_state != State.BLOCK:
			action_id += 1
			var my_id = action_id
			current_state = State.HIT
			_play_anim("Hit", 0.08, true)
			get_tree().create_timer(0.3).timeout.connect(func():
				if is_instance_valid(self) and my_id == action_id and current_state == State.HIT and not is_dead:
					current_state = State.IDLE
					_play_anim("Idle", 0.14)
			)

func _die():
	action_id += 1
	is_dead = true
	current_state = State.DEAD
	velocity = Vector3.ZERO
	_play_anim("Death", 0.1, true)
	emit_signal("died")

func _play_anim(anim_name: String, blend: float = 0.14, force_restart: bool = false):
	if anim_player and anim_player.has_animation(anim_name):
		if not force_restart and anim_player.current_animation == anim_name and anim_player.is_playing():
			return
		anim_player.play(anim_name, blend)
