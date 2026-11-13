class_name AutoFit
extends Node3D
## Instantiates a GLB, scales it so its largest-extent (height by default) matches
## target_size, centres it on X/Z and sits it on y=0. Works with arbitrary
## Sketchfab model scales/origins.

@export_file("*.glb") var model_path: String = ""
@export var target_size: float = 2.0
@export var fit_axis: String = "y"   # "y" = height, "max" = largest dimension
@export var yaw_degrees: float = 0.0
@export var tint: Color = Color(1, 1, 1, 0)  # alpha 0 = no tint

var model: Node3D

func _ready():
	if model_path != "":
		load_model(model_path)

static func collect_aabb(n: Node, xf: Transform3D, acc: Array):
	var t = xf
	if n is Node3D:
		t = xf * n.transform
	if n is MeshInstance3D and n.mesh:
		var b: AABB = t * n.mesh.get_aabb()
		acc[0] = b if acc[0] == null else acc[0].merge(b)
	for c in n.get_children():
		collect_aabb(c, t, acc)

func load_model(path: String):
	if model and is_instance_valid(model):
		model.queue_free()
	var scene = load(path)
	if scene == null:
		push_warning("AutoFit: cannot load " + path)
		return
	var inst = scene.instantiate()
	var holder = Node3D.new()
	add_child(holder)
	holder.add_child(inst)
	var acc = [null]
	collect_aabb(inst, Transform3D.IDENTITY, acc)
	if acc[0] == null:
		model = holder
		return
	var b: AABB = acc[0]
	var ext = b.size.y if fit_axis == "y" else max(b.size.x, max(b.size.y, b.size.z))
	var s = target_size / max(ext, 0.0001)
	inst.scale = Vector3.ONE * s
	var c = b.get_center() * s
	inst.position = Vector3(-c.x, -b.position.y * s, -c.z)
	holder.rotation_degrees.y = yaw_degrees
	if tint.a > 0.0:
		_apply_tint(inst, tint)
	model = holder

func _apply_tint(n: Node, col: Color):
	if n is MeshInstance3D:
		n.material_overlay = null
		var m = n.get_active_material(0)
		if m is StandardMaterial3D:
			var d = m.duplicate()
			d.albedo_color = d.albedo_color * col
			n.set_surface_override_material(0, d)
	for c in n.get_children():
		_apply_tint(c, col)

var _t := 0.0
func _process(delta):
	# Procedural walk bob for static (un-animated) Sketchfab characters.
	var p = get_parent()
	if model == null or not (p is CharacterBody3D):
		return
	var spd = Vector2(p.velocity.x, p.velocity.z).length()
	if spd > 0.5:
		_t += delta * clamp(spd, 2.0, 9.0) * 1.6
		model.position.y = abs(sin(_t)) * 0.12
		model.rotation.z = sin(_t) * 0.06
	else:
		model.position.y = lerp(model.position.y, 0.0, 10.0 * delta)
		model.rotation.z = lerp(model.rotation.z, 0.0, 10.0 * delta)
