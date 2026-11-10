extends Node3D

var damage: float = 50.0
var radius: float = 6.0
var lifetime: float = 0.7
var elapsed: float = 0.0

@onready var mesh = $MeshInstance3D
@onready var light = $OmniLight3D

func activate():
	var player = get_tree().get_first_node_in_group("player")
	if player:
		player.activate_ares_buff(8.0)

	var enemies = get_tree().get_nodes_in_group("enemies")
	for enemy in enemies:
		if is_instance_valid(enemy):
			var dist = global_position.distance_to(enemy.global_position)
			if dist <= radius:
				var dir = (enemy.global_position - global_position).normalized()
				enemy.take_damage(damage, dir * 18.0 + Vector3.UP * 4.0, "ares")

func _process(delta):
	elapsed += delta
	var progress = elapsed / lifetime
	if mesh:
		var s = lerp(0.5, radius * 2.0, progress)
		mesh.scale = Vector3(s, s * 0.4, s)
	if light:
		light.light_energy = max(0.0, 8.0 * (1.0 - progress))
	if elapsed >= lifetime:
		queue_free()
