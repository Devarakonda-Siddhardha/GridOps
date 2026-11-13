class_name Scenery
extends RefCounted
## Dresses a level with Sketchfab (CC-BY) architecture as non-colliding backdrop.

static func _add(parent: Node, path: String, pos: Vector3, size: float, yaw := 0.0, axis := "y"):
	var af = AutoFit.new()
	af.target_size = size
	af.fit_axis = axis
	af.yaw_degrees = yaw
	parent.add_child(af)
	af.position = pos
	af.load_model(path)

static func populate(level: Node, radius: float = 55.0):
	var root = Node3D.new()
	root.name = "SketchfabScenery"
	level.add_child(root)
	var temple = "res://assets/models/sf_temple_greco.glb"
	var cols = "res://assets/models/sf_doric_columns.glb"
	# ring of temples on the horizon
	for i in range(5):
		var a = deg_to_rad(200 + i * 35)
		_add(root, temple, Vector3(cos(a), 0, sin(a)) * radius, 16.0, rad_to_deg(-a) + 90, "max")
	# broken column rows flanking the arena
	for i in range(4):
		var a = deg_to_rad(15 + i * 90)
		_add(root, cols, Vector3(cos(a), 0, sin(a)) * (radius - 14), 6.0, rad_to_deg(-a), "y")
