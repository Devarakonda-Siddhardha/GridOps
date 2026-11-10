extends Node3D

var damage: float = 65.0
var radius: float = 7.0
var lifetime: float = 0.8
var elapsed: float = 0.0

@onready var mesh = $MeshInstance3D
@onready var light = $OmniLight3D

func activate():
	var player = get_tree().get_first_node_in_group("player")
	var total_heal: float = 0.0
	var enemies = get_tree().get_nodes_in_group("enemies")

	for enemy in enemies:
		if is_instance_valid(enemy):
			var dist = global_position.distance_to(enemy.global_position)
			if dist <= radius:
				var dir = (enemy.global_position - global_position).normalized()
				enemy.take_damage(damage, dir * 8.0, "soul")
				total_heal += damage * 0.45

	if player and total_heal > 0.0:
		player.heal(total_heal)

func _process(delta):
	elapsed += delta
	var progress = elapsed / lifetime
	if mesh:
		var s = lerp(1.0, radius * 2.0, progress)
		mesh.scale = Vector3(s, 0.2, s)
	if light:
		light.light_energy = max(0.0, 6.0 * (1.0 - progress))
	if elapsed >= lifetime:
		queue_free()
