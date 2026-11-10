extends Node3D

var speed: float = 16.0
var damage: float = 75.0
var lifetime: float = 1.2
var elapsed: float = 0.0
var direction: Vector3 = Vector3.FORWARD
var hit_enemies = []

@onready var mesh = $MeshInstance3D

func _ready():
	pass

func setup(dir: Vector3):
	direction = dir.normalized()
	if direction.length_squared() > 0.001:
		look_at(global_position + direction, Vector3.UP)

func _process(delta):
	elapsed += delta
	global_position += direction * speed * delta

	# Check enemies in front
	var enemies = get_tree().get_nodes_in_group("enemies")
	for enemy in enemies:
		if is_instance_valid(enemy) and not enemy in hit_enemies:
			var dist = global_position.distance_to(enemy.global_position)
			if dist <= 3.2:
				hit_enemies.append(enemy)
				var knockback = direction * 22.0 + Vector3.UP * 4.0
				enemy.take_damage(damage, knockback, "water")

	if elapsed >= lifetime:
		queue_free()
