extends CharacterBody3D

signal died(soldier)

enum State { IDLE, CHASE, RETREAT, ATTACK, HIT, DEAD }

@export var max_health: float = 65.0
@export var speed: float = 5.2
@export var shoot_range: float = 24.0
@export var retreat_range: float = 7.0
@export var arrow_damage: float = 18.0

var current_health: float = 65.0
var current_state: State = State.IDLE
var target: Node3D = null
var shoot_timer: float = 1.8
var is_dead: bool = false
var gravity: float = 24.0

var arrow_scene = preload("res://src/player/arrow.tscn")

@onready var anim_player: AnimationPlayer = $Model/AnimationPlayer
@onready var hp_label: Label3D = $HpLabel

func _ready():
	add_to_group("enemies")
	current_health = max_health
	_update_hp_display()
	_play_anim("Idle")

func _physics_process(delta):
	if is_dead:
		return

	if not is_on_floor():
		velocity.y -= gravity * delta

	if shoot_timer > 0.0:
		shoot_timer -= delta

	target = _find_best_target()
	if target:
		var dist = global_position.distance_to(target.global_position)
		var dir = (target.global_position - global_position).normalized()
		dir.y = 0

		match current_state:
			State.IDLE, State.CHASE, State.RETREAT:
				if dist < retreat_range:
					current_state = State.RETREAT
					velocity.x = -dir.x * speed
					velocity.z = -dir.z * speed
					rotation.y = lerp_angle(rotation.y, atan2(-dir.x, -dir.z), 10.0 * delta)
					_play_anim("Run")
				elif dist > shoot_range:
					current_state = State.CHASE
					velocity.x = dir.x * speed
					velocity.z = dir.z * speed
					rotation.y = lerp_angle(rotation.y, atan2(-dir.x, -dir.z), 10.0 * delta)
					_play_anim("Run")
				else:
					velocity.x = move_toward(velocity.x, 0, 15.0 * delta)
					velocity.z = move_toward(velocity.z, 0, 15.0 * delta)
					rotation.y = lerp_angle(rotation.y, atan2(-dir.x, -dir.z), 12.0 * delta)
					if shoot_timer <= 0.0:
						_shoot_arrow(dir)
					else:
						_play_anim("Idle")

			State.ATTACK:
				velocity.x = move_toward(velocity.x, 0, 20.0 * delta)
				velocity.z = move_toward(velocity.z, 0, 20.0 * delta)

			State.HIT:
				velocity.x = move_toward(velocity.x, 0, 18.0 * delta)
				velocity.z = move_toward(velocity.z, 0, 18.0 * delta)

	move_and_slide()

func _shoot_arrow(dir: Vector3):
	current_state = State.ATTACK
	shoot_timer = randf_range(2.0, 2.8)
	_play_anim("Attack")

	if randf() < 0.2:
		SoundManager.play_dialogue("roman_archer_shout")

	await get_tree().create_timer(0.35).timeout
	if is_dead:
		return

	var arrow = arrow_scene.instantiate()
	arrow.direction = dir.normalized()
	arrow.speed = 32.0
	arrow.damage = arrow_damage
	arrow.is_enemy_arrow = true
	get_parent().add_child(arrow)
	arrow.global_position = global_position + Vector3(0, 1.3, 0)
	SoundManager.play("arrow_shoot", randf_range(0.95, 1.05))

	await get_tree().create_timer(0.3).timeout
	if current_state == State.ATTACK:
		current_state = State.IDLE
		_play_anim("Idle")

func _find_best_target() -> Node3D:
	var player = get_tree().get_first_node_in_group("player")
	if player and not (player.has_method("is_dead") and player.is_dead):
		return player
	var allies = get_tree().get_nodes_in_group("allies")
	if allies.size() > 0:
		return allies[0]
	return null

func take_damage(amount: float, attacker_pos: Vector3 = Vector3.ZERO):
	if is_dead:
		return

	current_health = max(0.0, current_health - amount)
	_update_hp_display()
	_spawn_damage_number(amount)
	SoundManager.play("sword_hit", randf_range(0.9, 1.1))

	if attacker_pos != Vector3.ZERO:
		var knock = (global_position - attacker_pos).normalized()
		knock.y = 0
		velocity = knock * 6.0

	if current_health <= 0.0:
		_die()
	else:
		current_state = State.HIT
		_play_anim("Hit")
		await get_tree().create_timer(0.2).timeout
		if current_state == State.HIT:
			current_state = State.IDLE

func _die():
	is_dead = true
	current_state = State.DEAD
	if hp_label:
		hp_label.visible = false
	_play_anim("Death")
	emit_signal("died", self)
	$CollisionShape3D.set_deferred("disabled", true)
	get_tree().create_timer(2.0).timeout.connect(queue_free)

func _update_hp_display():
	if hp_label:
		var pct = int((current_health / max_health) * 100)
		var bar = ""
		var filled = int(pct / 10)
		for i in range(10):
			bar += "■" if i < filled else "□"
		hp_label.text = "Roman Sagittarii\n[%s] %d HP" % [bar, int(current_health)]

func _spawn_damage_number(amount: float):
	var root = get_tree().current_scene
	var lbl = Label3D.new()
	lbl.billboard = BaseMaterial3D.BILLBOARD_ENABLED
	lbl.text = "-%d" % int(amount)
	lbl.modulate = Color(1.0, 0.4, 0.4)
	lbl.outline_modulate = Color(0, 0, 0)
	lbl.outline_size = 8
	lbl.font_size = 32
	lbl.position = global_position + Vector3(randf_range(-0.4, 0.4), 2.2, randf_range(-0.4, 0.4))
	root.add_child(lbl)
	var tw = lbl.create_tween()
	tw.tween_property(lbl, "position:y", lbl.position.y + 1.2, 0.6)
	tw.parallel().tween_property(lbl, "modulate:a", 0.0, 0.6)
	tw.tween_callback(lbl.queue_free)

func _play_anim(anim_name: String):
	if anim_player and anim_player.has_animation(anim_name):
		anim_player.play(anim_name)
