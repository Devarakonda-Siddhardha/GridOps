extends CharacterBody3D

signal died(demon)

enum State { IDLE, CHASE, ATTACK, HIT, DEAD }

@export var max_health: float = 100.0
@export var speed: float = 4.8
@export var attack_damage: float = 18.0
@export var attack_range: float = 2.2
@export var attack_cooldown: float = 1.8
@export var is_boss: bool = false

var current_health: float = 100.0
var current_state: State = State.IDLE
var attack_timer: float = 0.0
var is_dead: bool = false
var gravity: float = 24.0

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

	attack_timer = max(0.0, attack_timer - delta)

	var player = get_tree().get_first_node_in_group("player")
	if not player or player.is_dead:
		velocity.x = move_toward(velocity.x, 0, 10.0 * delta)
		velocity.z = move_toward(velocity.z, 0, 10.0 * delta)
		move_and_slide()
		if current_state != State.IDLE:
			current_state = State.IDLE
			_play_anim("Idle")
		return

	var to_player = player.global_position - global_position
	to_player.y = 0
	var dist = to_player.length()

	match current_state:
		State.IDLE, State.CHASE:
			if dist > attack_range:
				var dir = to_player.normalized()
				velocity.x = dir.x * speed
				velocity.z = dir.z * speed
				# Face moving direction
				var target_angle = atan2(dir.x, dir.z)
				rotation.y = lerp_angle(rotation.y, target_angle, 10.0 * delta)
				if current_state != State.CHASE:
					current_state = State.CHASE
					_play_anim("Walk")
			else:
				velocity.x = move_toward(velocity.x, 0, 15.0 * delta)
				velocity.z = move_toward(velocity.z, 0, 15.0 * delta)
				if attack_timer <= 0.0:
					_start_attack(player)
				else:
					if current_state != State.IDLE:
						current_state = State.IDLE
						_play_anim("Idle")
			move_and_slide()

		State.ATTACK:
			velocity.x = move_toward(velocity.x, 0, 15.0 * delta)
			velocity.z = move_toward(velocity.z, 0, 15.0 * delta)
			move_and_slide()

		State.HIT:
			velocity.x = move_toward(velocity.x, 0, 14.0 * delta)
			velocity.z = move_toward(velocity.z, 0, 14.0 * delta)
			move_and_slide()

func _start_attack(player):
	current_state = State.ATTACK
	attack_timer = attack_cooldown
	_play_anim("Attack")
	SoundManager.play("demon_roar", 1.1 if not is_boss else 0.8)

	# Face player directly
	var dir = (player.global_position - global_position).normalized()
	rotation.y = atan2(dir.x, dir.z)

	# Strike frame at 0.35s
	get_tree().create_timer(0.35).timeout.connect(func():
		if current_state == State.ATTACK and not is_dead and is_instance_valid(player):
			var d = global_position.distance_to(player.global_position)
			if d <= attack_range + 0.6:
				var knock = (player.global_position - global_position).normalized() * 12.0
				player.take_damage(attack_damage, knock)
	)

	# Return to chase
	get_tree().create_timer(0.85).timeout.connect(func():
		if current_state == State.ATTACK and not is_dead:
			current_state = State.IDLE
	)

func take_damage(amount: float, knockback: Vector3, damage_type: String):
	if is_dead:
		return

	current_health = max(0.0, current_health - amount)
	_update_hp_display()
	_spawn_damage_number(amount, damage_type)

	velocity += knockback

	if current_health <= 0.0:
		_die()
	else:
		if current_state != State.ATTACK:
			current_state = State.HIT
			_play_anim("Hit")
			get_tree().create_timer(0.4).timeout.connect(func():
				if current_state == State.HIT and not is_dead:
					current_state = State.IDLE
			)

func _die():
	is_dead = true
	current_state = State.DEAD
	velocity = Vector3.ZERO
	if hp_label:
		hp_label.visible = false
	_play_anim("Death")
	SoundManager.play("demon_death", 1.0 if not is_boss else 0.7)
	if is_boss or randf() < 0.25:
		SoundManager.play_dialogue("demon_defeat")
	emit_signal("died", self)

	# Disable collision
	$CollisionShape3D.set_deferred("disabled", true)

	# Fade out after animation finishes
	get_tree().create_timer(1.8).timeout.connect(func():
		queue_free()
	)

func _update_hp_display():
	if hp_label:
		var pct = int((current_health / max_health) * 100)
		var bar = ""
		var filled = int(pct / 10)
		for i in range(10):
			bar += "■" if i < filled else "□"
		hp_label.text = "%s\n[%s] %d HP" % ["Tartarus Brute" if is_boss else "Tartarus Demon", bar, int(current_health)]

func _spawn_damage_number(amount: float, damage_type: String):
	var root = get_tree().current_scene
	var floating_lbl = Label3D.new()
	floating_lbl.billboard = BaseMaterial3D.BILLBOARD_ENABLED
	floating_lbl.font_size = 40 if amount > 80 else 32
	floating_lbl.outline_size = 8
	floating_lbl.text = str(int(amount))

	# Color based on damage source
	match damage_type:
		"lightning":
			floating_lbl.modulate = Color(0.4, 0.85, 1.0)
		"water":
			floating_lbl.modulate = Color(0.2, 0.9, 0.9)
		"soul":
			floating_lbl.modulate = Color(0.8, 0.2, 1.0)
		"ares":
			floating_lbl.modulate = Color(1.0, 0.25, 0.1)
		_:
			floating_lbl.modulate = Color(1.0, 0.9, 0.2)

	root.add_child(floating_lbl)
	floating_lbl.global_position = global_position + Vector3(randf_range(-0.4, 0.4), 2.4, randf_range(-0.4, 0.4))

	# Animate rising and fading
	var tween = root.create_tween()
	tween.tween_property(floating_lbl, "global_position:y", floating_lbl.global_position.y + 1.6, 0.65)
	tween.parallel().tween_property(floating_lbl, "modulate:a", 0.0, 0.65)
	tween.tween_callback(floating_lbl.queue_free)

func _play_anim(anim_name: String):
	if anim_player and anim_player.has_animation(anim_name):
		anim_player.play(anim_name)
