extends CharacterBody3D

signal died(soldier)

enum State { IDLE, CHASE, ATTACK, BLOCK, HIT, DEAD }

@export var max_health: float = 85.0
@export var speed: float = 4.6
@export var attack_damage: float = 20.0
@export var attack_range: float = 2.2
@export var attack_cooldown: float = 1.7

var current_health: float = 85.0
var current_state: State = State.IDLE
var attack_timer: float = 0.0
var is_dead: bool = false
var gravity: float = 24.0
var block_chance: float = 0.45

var target: Node3D = null

@onready var anim_player: AnimationPlayer = $Model/AnimationPlayer
@onready var hp_label: Label3D = $HpLabel

func _ready():
	add_to_group("enemies")
	floor_max_angle = deg_to_rad(60.0)
	floor_snap_length = 0.35
	floor_constant_speed = true
	floor_stop_on_slope = true
	current_health = max_health
	_update_hp_display()
	_play_anim("Idle")

func _physics_process(delta):
	if is_dead:
		return

	if not is_on_floor():
		velocity.y -= gravity * delta

	attack_timer = max(0.0, attack_timer - delta)

	# Find target: nearest Greek ally or player
	target = _find_best_target()
	if not target or (target.has_method("is_dead") and target.is_dead):
		velocity.x = move_toward(velocity.x, 0, 10.0 * delta)
		velocity.z = move_toward(velocity.z, 0, 10.0 * delta)
		move_and_slide()
		if current_state != State.IDLE:
			current_state = State.IDLE
			_play_anim("Idle")
		return

	var to_target = target.global_position - global_position
	to_target.y = 0
	var dist = to_target.length()

	match current_state:
		State.IDLE, State.CHASE:
			if dist > attack_range:
				var dir = to_target.normalized()
				velocity.x = dir.x * speed
				velocity.z = dir.z * speed
				var target_angle = atan2(-dir.x, -dir.z)
				rotation.y = lerp_angle(rotation.y, target_angle, 10.0 * delta)
				_play_anim("Run")
			else:
				velocity.x = 0
				velocity.z = 0
				if attack_timer <= 0.0:
					_start_attack()
				else:
					_play_anim("Idle")

		State.ATTACK:
			velocity.x = move_toward(velocity.x, 0, 12.0 * delta)
			velocity.z = move_toward(velocity.z, 0, 12.0 * delta)

		State.BLOCK:
			velocity.x = move_toward(velocity.x, 0, 14.0 * delta)
			velocity.z = move_toward(velocity.z, 0, 14.0 * delta)

		State.HIT:
			velocity.x = move_toward(velocity.x, 0, 18.0 * delta)
			velocity.z = move_toward(velocity.z, 0, 18.0 * delta)

	move_and_slide()

func _find_best_target() -> Node3D:
	var player = get_tree().get_first_node_in_group("player")
	var allies = get_tree().get_nodes_in_group("allies")

	var best = player
	var min_d = global_position.distance_to(player.global_position) if player and not player.is_dead else 9999.0

	for a in allies:
		if is_instance_valid(a) and not (a.get("is_dead") == true):
			var d = global_position.distance_to(a.global_position)
			if d < min_d:
				min_d = d
				best = a
	return best

func _start_attack():
	current_state = State.ATTACK
	attack_timer = attack_cooldown
	_play_anim("Attack")
	SoundManager.play("sword_swing", 0.95)

	get_tree().create_timer(0.35).timeout.connect(func():
		if current_state == State.ATTACK and not is_dead and is_instance_valid(target):
			var d = global_position.distance_to(target.global_position)
			if d <= attack_range + 0.8:
				if target.has_method("take_damage"):
					var forward = -transform.basis.z
					target.take_damage(attack_damage, forward * 10.0 + Vector3.UP * 2.0)
					SoundManager.play("sword_hit", 1.0)
	)

	get_tree().create_timer(0.75).timeout.connect(func():
		if current_state == State.ATTACK and not is_dead:
			current_state = State.CHASE
	)

func take_damage(amount: float, knockback: Vector3 = Vector3.ZERO, damage_type: String = "melee"):
	if is_dead:
		return

	# Scutum Shield Block check for frontal melee
	if damage_type == "melee" and randf() < block_chance and current_state != State.BLOCK:
		current_state = State.BLOCK
		_play_anim("ShieldBlock")
		SoundManager.play("shield_block", 1.0)
		_spawn_damage_number(0, "blocked")
		velocity += knockback * 0.15
		get_tree().create_timer(0.5).timeout.connect(func():
			if current_state == State.BLOCK and not is_dead:
				current_state = State.CHASE
		)
		return

	current_health = max(0.0, current_health - amount)
	_update_hp_display()
	_spawn_damage_number(amount, damage_type)
	velocity += knockback * 0.45

	if current_health <= 0.0:
		_die()
	else:
		if current_state != State.ATTACK:
			current_state = State.HIT
			_play_anim("Hit")
			get_tree().create_timer(0.35).timeout.connect(func():
				if current_state == State.HIT and not is_dead:
					current_state = State.CHASE
			)

func _die():
	is_dead = true
	current_state = State.DEAD
	velocity = Vector3.ZERO
	if hp_label:
		hp_label.visible = false
	_play_anim("Death")
	SoundManager.play("sword_hit", 0.7)
	emit_signal("died", self)

	$CollisionShape3D.set_deferred("disabled", true)
	get_tree().create_timer(2.5).timeout.connect(queue_free)

func _update_hp_display():
	if hp_label:
		var pct = int((current_health / max_health) * 100)
		var bar = ""
		var filled = int(pct / 10)
		for i in range(10):
			bar += "■" if i < filled else "□"
		hp_label.text = "Roman Legionnaire\n[%s] %d HP" % [bar, int(current_health)]

func _spawn_damage_number(amount: float, damage_type: String):
	var root = get_tree().current_scene
	var lbl = Label3D.new()
	lbl.billboard = BaseMaterial3D.BILLBOARD_ENABLED
	lbl.font_size = 32
	lbl.outline_size = 6
	lbl.text = "BLOCKED!" if damage_type == "blocked" else str(int(amount))
	lbl.modulate = Color(0.7, 0.7, 0.7) if damage_type == "blocked" else Color(1.0, 0.3, 0.2)
	root.add_child(lbl)
	lbl.global_position = global_position + Vector3(randf_range(-0.3, 0.3), 2.2, randf_range(-0.3, 0.3))

	var tween = root.create_tween()
	tween.tween_property(lbl, "global_position:y", lbl.global_position.y + 1.4, 0.6)
	tween.parallel().tween_property(lbl, "modulate:a", 0.0, 0.6)
	tween.tween_callback(lbl.queue_free)

func _play_anim(anim_name: String):
	if anim_player and anim_player.has_animation(anim_name):
		anim_player.play(anim_name)
