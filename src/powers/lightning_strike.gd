extends Node3D

var damage: float = 120.0
var radius: float = 4.0
var lifetime: float = 0.6
var elapsed: float = 0.0

@onready var area = $Area3D
@onready var light = $OmniLight3D

func activate():
	# Damage nearby demons immediately upon strike
	var enemies = get_tree().get_nodes_in_group("enemies")
	for enemy in enemies:
		if is_instance_valid(enemy):
			var dist = global_position.distance_to(enemy.global_position)
			if dist <= radius:
				var dir = (enemy.global_position - global_position).normalized()
				enemy.take_damage(damage, dir * 14.0, "lightning")

func _process(delta):
	elapsed += delta
	if light:
		light.light_energy = max(0.0, 8.0 * (1.0 - (elapsed / lifetime)))
	if elapsed >= lifetime:
		queue_free()
