extends CharacterBody3D

signal died(boss)

enum State { IDLE, CHASE, SLAM_ATTACK, GORE_ATTACK, HIT, DEAD }

@export var max_health: float = 650.0
@export var speed: float = 5.5
@export var slam_damage: float = 42.0
@export var slam_radius: float = 7.5

var current_health: float = 650.0
var current_state: State = State.IDLE
var target: Node3D = null
var attack_cooldown: float = 2.0
var is_dead: bool = false
var gravity: float = 24.0

@onready var anim_player: AnimationPlayer = $Model/AnimationPlayer
@onready var hp_label: Label3D = $HpLabel

func _ready():
	add_to_group("enemies")
	add_to_group("bosses")
	current_health = max_health
	_update_hp_display()
	_play_anim("Idle")
	SoundManager.play_dialogue("minotaur_bellow")
	DivineManager.emit_signal("boss_spawned", "INFERNAL MINOTAUR", max_health)

func _physics_process(delta):
	if is_dead:
		return

	if not is_on_floor():
		velocity.y -= gravity * delta

	if attack_cooldown > 0.0:
		attack_cooldown -= delta

	target = _find_best_target()
	if target:
		var dist = global_position.distance_to(target.global_position)
		var dir = (target.global_position - global_position).normalized()
		dir.y = 0

		match current_state:
			State.IDLE, State.CHASE:
				if dist <= 5.0 and attack_cooldown <= 0.0:
					_start_ground_slam()
				else:
					current_state = State.CHASE
					velocity.x = dir.x * speed
					velocity.z = dir.z * speed
					rotation.y = lerp_angle(rotation.y, atan2(-dir.x, -dir.z), 6.0 * delta)
					_play_anim("Run")

			State.SLAM_ATTACK:
				velocity.x = move_toward(velocity.x, 0, 20.0 * delta)
				velocity.z = move_toward(velocity.z, 0, 20.0 * delta)

			State.HIT:
				velocity.x = move_toward(velocity.x, 0, 15.0 * delta)
				velocity.z = move_toward(velocity.z, 0, 15.0 * delta)

	move_and_slide()

func _start_ground_slam():
	current_state = State.SLAM_ATTACK
	attack_cooldown = 3.5
	_play_anim("Attack")

	# Wind up overhead
	await get_tree().create_timer(0.4).timeout
	if is_dead:
		return

	# Slam impact!
	SoundManager.play("minotaur_slam", randf_range(0.9, 1.05))
	DivineManager.emit_signal("camera_shake_requested", 1.2, 0.4)

	# Radial shockwave damage
	var space_state = get_world_3d().direct_space_state
	var query = PhysicsShapeQueryParameters3D.new()
	var sphere = SphereShape3D.new()
	sphere.radius = slam_radius
	query.shape = sphere
	query.transform = Transform3D(Basis.IDENTITY, global_position + Vector3(0, 0.5, 0))
	query.collision_mask = 1 | 2 # Player & Allies

	var hits = space_state.intersect_shape(query, 16)
	for h in hits:
		var col = h.collider
		if col and col.has_method("take_damage"):
			col.take_damage(slam_damage, global_position)

	await get_tree().create_timer(0.5).timeout
	if current_state == State.SLAM_ATTACK:
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
	DivineManager.emit_signal("boss_health_updated", current_health, max_health)
	_spawn_damage_number(amount)
	SoundManager.play("sword_hit", randf_range(0.85, 0.95))

	if current_health <= 0.0:
		_die()
	else:
		if current_state != State.SLAM_ATTACK and randf() < 0.2:
			current_state = State.HIT
			_play_anim("Hit")
			await get_tree().create_timer(0.25).timeout
			if current_state == State.HIT:
				current_state = State.IDLE

func _die():
	is_dead = true
	current_state = State.DEAD
	if hp_label:
		hp_label.visible = false
	_play_anim("Death")
	DivineManager.emit_signal("boss_defeated")
	emit_signal("died", self)
	$CollisionShape3D.set_deferred("disabled", true)
	get_tree().create_timer(3.5).timeout.connect(queue_free)

func _update_hp_display():
	if hp_label:
		var pct = int((current_health / max_health) * 100)
		var bar = ""
		var filled = int(pct / 10)
		for i in range(10):
			bar += "■" if i < filled else "□"
		hp_label.text = "Infernal Minotaur\n[%s] %d HP" % [bar, int(current_health)]

func _spawn_damage_number(amount: float):
	var root = get_tree().current_scene
	var lbl = Label3D.new()
	lbl.billboard = BaseMaterial3D.BILLBOARD_ENABLED
	lbl.text = "-%d" % int(amount)
	lbl.modulate = Color(1.0, 0.2, 0.2)
	lbl.outline_modulate = Color(0, 0, 0)
	lbl.outline_size = 10
	lbl.font_size = 38
	lbl.position = global_position + Vector3(randf_range(-0.5, 0.5), 3.4, randf_range(-0.5, 0.5))
	root.add_child(lbl)
	var tw = lbl.create_tween()
	tw.tween_property(lbl, "position:y", lbl.position.y + 1.5, 0.7)
	tw.parallel().tween_property(lbl, "modulate:a", 0.0, 0.7)
	tw.tween_callback(lbl.queue_free)

func _play_anim(anim_name: String):
	if anim_player and anim_player.has_animation(anim_name):
		anim_player.play(anim_name)
