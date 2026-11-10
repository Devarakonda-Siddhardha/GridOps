extends CharacterBody3D

signal died(soldier)

enum State { FOLLOW, CHARGE, ATTACK, HIT, DEAD }

@export var max_health: float = 95.0
@export var speed: float = 5.6
@export var attack_damage: float = 35.0
@export var attack_range: float = 2.4
@export var squad_index: int = 0

var current_health: float = 95.0
var current_state: State = State.FOLLOW
var attack_timer: float = 0.0
var is_dead: bool = false
var gravity: float = 24.0

var formation_offset: Vector3 = Vector3.ZERO
var target_enemy: Node3D = null

@onready var anim_player: AnimationPlayer = $Model/AnimationPlayer
@onready var hp_label: Label3D = $HpLabel

func _ready():
	add_to_group("allies")
	current_health = max_health
	_update_hp_display()
	_play_anim("Idle")

	CampaignManager.connect("army_command", Callable(self, "_on_army_command"))
	_calculate_formation_offset()

func _calculate_formation_offset():
	# Phalanx formation: arrange in rows behind player
	var row = int(squad_index / 4) + 1
	var col = (squad_index % 4) - 1.5
	formation_offset = Vector3(col * 2.2, 0, row * 2.4)

func _physics_process(delta):
	if is_dead:
		return

	if not is_on_floor():
		velocity.y -= gravity * delta

	attack_timer = max(0.0, attack_timer - delta)

	var player = get_tree().get_first_node_in_group("player")
	if not player or player.is_dead:
		velocity.x = move_toward(velocity.x, 0, 10.0 * delta)
		velocity.z = move_toward(velocity.z, 0, 10.0 * delta)
		move_and_slide()
		return

	# State machine
	match current_state:
		State.FOLLOW:
			# If an enemy gets very close, auto-engage
			var nearest_e = _find_nearest_enemy(12.0)
			if nearest_e:
				target_enemy = nearest_e
				current_state = State.CHARGE
				return

			var target_pos = player.global_position + (player.transform.basis * formation_offset)
			var to_pos = target_pos - global_position
			to_pos.y = 0
			var dist = to_pos.length()

			if dist > 1.2:
				var dir = to_pos.normalized()
				velocity.x = dir.x * (speed * 1.15 if dist > 6.0 else speed)
				velocity.z = dir.z * (speed * 1.15 if dist > 6.0 else speed)
				var target_angle = atan2(dir.x, dir.z)
				rotation.y = lerp_angle(rotation.y, target_angle, 12.0 * delta)
				_play_anim("Run")
			else:
				velocity.x = move_toward(velocity.x, 0, 12.0 * delta)
				velocity.z = move_toward(velocity.z, 0, 12.0 * delta)
				rotation.y = lerp_angle(rotation.y, player.rotation.y, 8.0 * delta)
				_play_anim("Idle")

		State.CHARGE:
			if not is_instance_valid(target_enemy) or (target_enemy.has_method("is_dead") and target_enemy.is_dead):
				target_enemy = _find_nearest_enemy(32.0)
				if not target_enemy:
					current_state = State.FOLLOW
					return

			var to_enemy = target_enemy.global_position - global_position
			to_enemy.y = 0
			var dist = to_enemy.length()

			if dist > attack_range:
				var dir = to_enemy.normalized()
				velocity.x = dir.x * (speed * 1.2)
				velocity.z = dir.z * (speed * 1.2)
				var target_angle = atan2(dir.x, dir.z)
				rotation.y = lerp_angle(rotation.y, target_angle, 14.0 * delta)
				_play_anim("Run")
			else:
				velocity.x = 0
				velocity.z = 0
				if attack_timer <= 0.0:
					_start_attack()

		State.ATTACK:
			velocity.x = move_toward(velocity.x, 0, 14.0 * delta)
			velocity.z = move_toward(velocity.z, 0, 14.0 * delta)

		State.HIT:
			velocity.x = move_toward(velocity.x, 0, 18.0 * delta)
			velocity.z = move_toward(velocity.z, 0, 18.0 * delta)

	move_and_slide()

func _find_nearest_enemy(max_dist: float) -> Node3D:
	var enemies = get_tree().get_nodes_in_group("enemies")
	var nearest = null
	var min_d = max_dist
	for e in enemies:
		if is_instance_valid(e) and not (e.get("is_dead") == true):
			var d = global_position.distance_to(e.global_position)
			if d < min_d:
				min_d = d
				nearest = e
	return nearest

func _start_attack():
	current_state = State.ATTACK
	attack_timer = 1.3
	_play_anim("Attack")
	SoundManager.play("sword_swing", 1.1)

	get_tree().create_timer(0.35).timeout.connect(func():
		if current_state == State.ATTACK and not is_dead and is_instance_valid(target_enemy):
			var d = global_position.distance_to(target_enemy.global_position)
			if d <= attack_range + 0.8:
				if target_enemy.has_method("take_damage"):
					var forward = -transform.basis.z
					target_enemy.take_damage(attack_damage, forward * 10.0 + Vector3.UP * 2.0, "spear")
					SoundManager.play("sword_hit", 1.0)
	)

	get_tree().create_timer(0.8).timeout.connect(func():
		if current_state == State.ATTACK and not is_dead:
			current_state = State.CHARGE
	)

func take_damage(amount: float, knockback: Vector3 = Vector3.ZERO):
	if is_dead:
		return

	current_health = max(0.0, current_health - amount)
	_update_hp_display()
	SoundManager.play("sword_hit", 0.9)

	if current_health <= 0.0:
		_die()
	else:
		velocity += knockback * 0.4
		if current_state != State.ATTACK:
			current_state = State.HIT
			_play_anim("Hit")
			get_tree().create_timer(0.35).timeout.connect(func():
				if current_state == State.HIT and not is_dead:
					current_state = State.FOLLOW
			)

func _die():
	is_dead = true
	current_state = State.DEAD
	velocity = Vector3.ZERO
	if hp_label:
		hp_label.visible = false
	_play_anim("Death")
	SoundManager.play("player_hurt", 0.8)
	CampaignManager.ally_died()
	emit_signal("died", self)

	$CollisionShape3D.set_deferred("disabled", true)
	get_tree().create_timer(3.0).timeout.connect(queue_free)

func _update_hp_display():
	if hp_label:
		var pct = int((current_health / max_health) * 100)
		var bar = ""
		var filled = int(pct / 10)
		for i in range(10):
			bar += "■" if i < filled else "□"
		hp_label.text = "Greek Hoplite\n[%s] %d HP" % [bar, int(current_health)]

func _on_army_command(cmd: String):
	if is_dead:
		return
	if cmd == "charge":
		target_enemy = _find_nearest_enemy(60.0)
		current_state = State.CHARGE
	elif cmd == "regroup":
		target_enemy = null
		current_state = State.FOLLOW

func _play_anim(anim_name: String):
	if anim_player and anim_player.has_animation(anim_name):
		anim_player.play(anim_name)
