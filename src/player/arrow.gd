extends Area3D

@export var speed: float = 38.0
@export var damage: float = 35.0
@export var is_enemy_arrow: bool = false
@export var is_fire_arrow: bool = false

var direction: Vector3 = Vector3.FORWARD
var lifetime: float = 4.0

func _ready():
	monitoring = true
	body_entered.connect(_on_body_entered)
	area_entered.connect(_on_area_entered)
	if is_fire_arrow:
		damage *= 1.8
		$FireGlow.visible = true

func _process(delta):
	global_position += direction * speed * delta
	lifetime -= delta
	if lifetime <= 0.0:
		queue_free()

func _on_body_entered(body: Node3D):
	_handle_hit(body)

func _on_area_entered(area: Area3D):
	_handle_hit(area.get_parent())

func _handle_hit(target: Node):
	if target == null:
		return

	if not is_enemy_arrow:
		# Player / Ally arrow hitting enemies or destructibles
		if target.is_in_group("enemies") and target.has_method("take_damage"):
			target.take_damage(damage, global_position)
			SoundManager.play("arrow_hit", randf_range(0.95, 1.05))
			queue_free()
		elif target.is_in_group("destructible") and target.has_method("take_damage"):
			target.take_damage(damage)
			SoundManager.play("arrow_hit", randf_range(0.95, 1.05))
			queue_free()
		elif target.is_in_group("environment") or target is StaticBody3D:
			SoundManager.play("arrow_hit", randf_range(0.9, 1.1))
			queue_free()
	else:
		# Enemy arrow hitting player or allies
		if target.is_in_group("player") and target.has_method("take_damage"):
			target.take_damage(damage, global_position)
			SoundManager.play("arrow_hit", randf_range(0.95, 1.05))
			queue_free()
		elif target.is_in_group("allies") and target.has_method("take_damage"):
			target.take_damage(damage, global_position)
			SoundManager.play("arrow_hit", randf_range(0.95, 1.05))
			queue_free()
		elif target is StaticBody3D:
			queue_free()
