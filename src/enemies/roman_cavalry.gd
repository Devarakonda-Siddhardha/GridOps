extends CharacterBody3D

signal died(soldier)

enum State { IDLE, CHASE, CHARGE, HIT, DEAD }

@export var max_health: float = 175.0
@export var speed: float = 9.8
@export var charge_damage: float = 28.0
@export var charge_range: float = 15.0

var current_health: float = 175.0
var current_state: State = State.IDLE
var target: Node3D = null
var charge_cooldown: float = 2.5
var is_dead: bool = false
var gravity: float = 24.0
var gallop_timer: float = 0.0

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

	if charge_cooldown > 0.0:
		charge_cooldown -= delta

	target = _find_best_target()
	if target:
		var dist = global_position.distance_to(target.global_position)
		var dir = (target.global_position - global_position).normalized()
		dir.y = 0

		match current_state:
			State.IDLE, State.CHASE:
				if dist <= charge_range and charge_cooldown <= 0.0:
					_start_charge(dir)
				else:
					current_state = State.CHASE
					velocity.x = dir.x * speed
					velocity.z = dir.z * speed
					rotation.y = lerp_angle(rotation.y, atan2(-dir.x, -dir.z), 8.0 * delta)
					_play_anim("Run")

					gallop_timer -= delta
					if gallop_timer <= 0.0:
						gallop_timer = 0.4
						SoundManager.play("horse_gallop", randf_range(0.9, 1.1), -6.0)

			State.CHARGE:
				# High-speed forward run during lance attack
				move_and_slide()

			State.HIT:
				velocity.x = move_toward(velocity.x, 0, 16.0 * delta)
				velocity.z = move_toward(velocity.z, 0, 16.0 * delta)
				move_and_slide()

	else:
		velocity.x = move_toward(velocity.x, 0, 10.0 * delta)
		velocity.z = move_toward(velocity.z, 0, 10.0 * delta)
		if current_state == State.CHASE:
			current_state = State.IDLE
			_play_anim("Idle")

	if current_state != State.CHARGE:
		move_and_slide()

func _start_charge(dir: Vector3):
	current_state = State.CHARGE
	charge_cooldown = 4.0
	rotation.y = atan2(-dir.x, -dir.z)
	velocity = dir * 14.0
	_play_anim("Attack")

	SoundManager.play("horse_neigh", 1.0)
	if randf() < 0.3:
		SoundManager.play_dialogue("roman_cavalry_charge")

	# Wait for lance impact frame
	await get_tree().create_timer(0.35).timeout
	if is_dead:
		return

	# Impact detection in front of cavalry
	var space_state = get_world_3d().direct_space_state
	var query = PhysicsShapeQueryParameters3D.new()
	var sphere = SphereShape3D.new()
	sphere.radius = 2.4
	query.shape = sphere
	query.transform = Transform3D(Basis.IDENTITY, global_position + dir * 2.0 + Vector3(0, 1.0, 0))
	query.collision_mask = 1 | 2 # Player or Allies

	var hits = space_state.intersect_shape(query, 8)
	for h in hits:
		var col = h.collider
		if col and (col.is_in_group("player") or col.is_in_group("allies")) and col.has_method("take_damage"):
			col.take_damage(charge_damage, global_position)
			SoundManager.play("lance_pierce", 1.0)

	await get_tree().create_timer(0.4).timeout
	if current_state == State.CHARGE:
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
		velocity = knock * 4.0

	if current_health <= 0.0:
		_die()
	else:
		if current_state != State.CHARGE:
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
	SoundManager.play("horse_neigh", 0.7)
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
		hp_label.text = "Roman Equites\n[%s] %d HP" % [bar, int(current_health)]

func _spawn_damage_number(amount: float):
	var root = get_tree().current_scene
	var lbl = Label3D.new()
	lbl.billboard = BaseMaterial3D.BILLBOARD_ENABLED
	lbl.text = "-%d" % int(amount)
	lbl.modulate = Color(1.0, 0.3, 0.3)
	lbl.outline_modulate = Color(0, 0, 0)
	lbl.outline_size = 8
	lbl.font_size = 32
	lbl.position = global_position + Vector3(randf_range(-0.4, 0.4), 2.5, randf_range(-0.4, 0.4))
	root.add_child(lbl)
	var tw = lbl.create_tween()
	tw.tween_property(lbl, "position:y", lbl.position.y + 1.2, 0.6)
	tw.parallel().tween_property(lbl, "modulate:a", 0.0, 0.6)
	tw.tween_callback(lbl.queue_free)

func _play_anim(anim_name: String):
	if anim_player and anim_player.has_animation(anim_name):
		anim_player.play(anim_name)
