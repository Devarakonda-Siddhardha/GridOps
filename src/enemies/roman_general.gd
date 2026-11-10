extends CharacterBody3D

signal boss_health_changed(current: float, max_val: float)
signal died(general)

enum State { IDLE, INTRO, CHASE, ATTACK, SHIELD_SLAM, TESTUDO, HIT, DEAD }

@export var max_health: float = 850.0
@export var speed: float = 5.2
@export var attack_damage: float = 45.0
@export var attack_range: float = 3.0

var current_health: float = 850.0
var current_state: State = State.IDLE
var attack_timer: float = 0.0
var special_timer: float = 4.0
var is_dead: bool = false
var gravity: float = 24.0

var phase2_triggered: bool = false
var has_introduced: bool = false

var target: Node3D = null

@onready var anim_player: AnimationPlayer = $Model/AnimationPlayer
@onready var hp_label: Label3D = $HpLabel

func _ready():
	add_to_group("enemies")
	add_to_group("bosses")
	floor_max_angle = deg_to_rad(60.0)
	floor_snap_length = 0.35
	floor_constant_speed = true
	floor_stop_on_slope = true
	current_health = max_health
	emit_signal("boss_health_changed", current_health, max_health)
	_update_hp_display()
	_play_anim("Idle")

func _physics_process(delta):
	if is_dead:
		return

	if not is_on_floor():
		velocity.y -= gravity * delta

	attack_timer = max(0.0, attack_timer - delta)
	special_timer = max(0.0, special_timer - delta)

	target = _find_best_target()
	if not target:
		velocity.x = move_toward(velocity.x, 0, 10.0 * delta)
		velocity.z = move_toward(velocity.z, 0, 10.0 * delta)
		move_and_slide()
		return

	# Trigger intro voice line when player gets in range
	if not has_introduced:
		var player = get_tree().get_first_node_in_group("player")
		if player and global_position.distance_to(player.global_position) < 22.0:
			has_introduced = true
			SoundManager.play_dialogue("general_intro")

	# Phase 2 trigger (<50% HP)
	if not phase2_triggered and current_health <= max_health * 0.5:
		_trigger_phase_two()
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
				rotation.y = lerp_angle(rotation.y, target_angle, 8.0 * delta)
				_play_anim("Run")
			else:
				velocity.x = 0
				velocity.z = 0
				if special_timer <= 0.0:
					_start_shield_slam()
				elif attack_timer <= 0.0:
					_start_attack()
				else:
					_play_anim("Idle")

		State.ATTACK, State.SHIELD_SLAM, State.TESTUDO, State.HIT:
			velocity.x = move_toward(velocity.x, 0, 14.0 * delta)
			velocity.z = move_toward(velocity.z, 0, 14.0 * delta)

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
	attack_timer = 2.2
	_play_anim("Attack")
	SoundManager.play("sword_swing", 0.8)

	get_tree().create_timer(0.45).timeout.connect(func():
		if current_state == State.ATTACK and not is_dead and is_instance_valid(target):
			var d = global_position.distance_to(target.global_position)
			if d <= attack_range + 1.2:
				if target.has_method("take_damage"):
					var forward = -transform.basis.z
					target.take_damage(attack_damage, forward * 18.0 + Vector3.UP * 3.5)
					SoundManager.play("sword_hit", 0.9)
	)

	get_tree().create_timer(1.0).timeout.connect(func():
		if current_state == State.ATTACK and not is_dead:
			current_state = State.CHASE
	)

func _start_shield_slam():
	current_state = State.SHIELD_SLAM
	special_timer = 9.0
	_play_anim("ShieldBlock")
	SoundManager.play("shield_block", 0.8)

	get_tree().create_timer(0.4).timeout.connect(func():
		if not is_dead:
			# Area shockwave: hits player & allies in 6m radius
			SoundManager.play("ares_fury", 0.9)
			var targets = get_tree().get_nodes_in_group("allies")
			var player = get_tree().get_first_node_in_group("player")
			if player:
				targets.append(player)

			for t in targets:
				if is_instance_valid(t) and global_position.distance_to(t.global_position) < 6.5:
					var push_dir = (t.global_position - global_position).normalized()
					t.take_damage(50.0, push_dir * 24.0 + Vector3.UP * 4.0)
	)

	get_tree().create_timer(1.1).timeout.connect(func():
		if current_state == State.SHIELD_SLAM and not is_dead:
			current_state = State.CHASE
	)

func _trigger_phase_two():
	phase2_triggered = true
	current_state = State.TESTUDO
	_play_anim("WarHorn")
	SoundManager.play("war_horn_roman", 0.8)
	SoundManager.play_dialogue("general_testudo")
	DivineManager.emit_signal("message_broadcast", "GENERAL MARCUS - PHASE II!", "The Roman Legatus calls the Praetorian Guard!")

	# Spawn 4 Praetorian Legionnaires around him
	var soldier_scene = load("res://src/enemies/roman_soldier.tscn")
	var root = get_tree().current_scene
	for i in range(4):
		var angle = i * (PI / 2)
		var offset = Vector3(cos(angle) * 5.0, 0, sin(angle) * 5.0)
		var p = soldier_scene.instantiate()
		root.add_child(p)
		p.global_position = global_position + offset

	get_tree().create_timer(1.5).timeout.connect(func():
		if current_state == State.TESTUDO and not is_dead:
			speed = 6.0
			attack_damage = 55.0
			current_state = State.CHASE
	)

func take_damage(amount: float, knockback: Vector3 = Vector3.ZERO, damage_type: String = "melee"):
	if is_dead:
		return

	# General Marcus has heavy armor (25% damage mitigation)
	var final_dmg = amount * 0.75
	current_health = max(0.0, current_health - final_dmg)
	emit_signal("boss_health_changed", current_health, max_health)
	_update_hp_display()
	_spawn_damage_number(final_dmg, damage_type)
	velocity += knockback * 0.15

	if current_health <= 0.0:
		_die()
	else:
		if current_state != State.ATTACK and current_state != State.SHIELD_SLAM and current_state != State.TESTUDO:
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
	SoundManager.play("sword_hit", 0.5)
	SoundManager.play_dialogue("general_defeat")
	emit_signal("died", self)

	$CollisionShape3D.set_deferred("disabled", true)

func _update_hp_display():
	if hp_label:
		var pct = int((current_health / max_health) * 100)
		var bar = ""
		var filled = int(pct / 10)
		for i in range(10):
			bar += "■" if i < filled else "□"
		hp_label.text = "👑 GENERAL MARCUS AURELIUS 👑\n[%s] %d / %d HP" % [bar, int(current_health), int(max_health)]

func _spawn_damage_number(amount: float, damage_type: String):
	var root = get_tree().current_scene
	var lbl = Label3D.new()
	lbl.billboard = BaseMaterial3D.BILLBOARD_ENABLED
	lbl.font_size = 44
	lbl.outline_size = 8
	lbl.text = str(int(amount))
	lbl.modulate = Color(1.0, 0.8, 0.2)
	root.add_child(lbl)
	lbl.global_position = global_position + Vector3(0, 3.2, 0)
	var tween = root.create_tween()
	tween.tween_property(lbl, "global_position:y", lbl.global_position.y + 1.8, 0.7)
	tween.parallel().tween_property(lbl, "modulate:a", 0.0, 0.7)
	tween.tween_callback(lbl.queue_free)

func _play_anim(anim_name: String):
	if anim_player and anim_player.has_animation(anim_name):
		anim_player.play(anim_name)
