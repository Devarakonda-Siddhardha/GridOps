extends SceneTree

func _aabb(n: Node, xf: Transform3D, acc: Array):
	if n is MeshInstance3D and n.mesh:
		var t = xf * n.transform
		var b = t * n.mesh.get_aabb()
		acc[0] = b if acc[0] == null else acc[0].merge(b)
	for c in n.get_children():
		if c is Node3D:
			_aabb(c, xf * n.transform if n != null and n is Node3D and n.get_parent() != null else xf, acc)
		else:
			_aabb(c, xf, acc)

func _init():
	var dir = DirAccess.open("res://assets/models")
	for f in dir.get_files():
		if f.begins_with("sf_") and f.ends_with(".glb"):
			var inst = load("res://assets/models/" + f).instantiate()
			var acc = [null]
			_walk(inst, Transform3D.IDENTITY, acc)
			var b: AABB = acc[0]
			print("%s size=%s min=%s" % [f, b.size, b.position])
	quit()

func _walk(n: Node, xf: Transform3D, acc: Array):
	var t = xf
	if n is Node3D:
		t = xf * n.transform
	if n is MeshInstance3D and n.mesh:
		var b = t * n.mesh.get_aabb()
		acc[0] = b if acc[0] == null else acc[0].merge(b)
	for c in n.get_children():
		_walk(c, t, acc)
