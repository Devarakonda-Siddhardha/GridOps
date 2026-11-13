extends Node3D
# Contact sheet: all downloaded sf_* models fitted to 3m, in a row, labelled.

func _ready():
	var env = WorldEnvironment.new()
	var e = Environment.new()
	e.background_mode = Environment.BG_COLOR
	e.background_color = Color(0.25, 0.28, 0.35)
	e.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	e.ambient_light_color = Color(0.8, 0.8, 0.85)
	e.ambient_light_energy = 0.9
	env.environment = e
	add_child(env)
	var sun = DirectionalLight3D.new()
	sun.rotation_degrees = Vector3(-45, 35, 0)
	add_child(sun)

	var files = []
	for f in DirAccess.open("res://assets/models").get_files():
		if f.begins_with("sf_") and f.ends_with(".glb"):
			files.append(f)
	files.sort()
	var i = 0
	for f in files:
		var af = AutoFit.new()
		af.target_size = 3.0
		af.fit_axis = "max"
		af.position = Vector3((i % 5) * 4.0, 0, (i / 5) * -4.5)
		add_child(af)
		af.load_model("res://assets/models/" + f)
		var l = Label3D.new()
		l.text = f.replace("sf_", "").replace(".glb", "")
		l.billboard = BaseMaterial3D.BILLBOARD_ENABLED
		l.font_size = 48
		l.pixel_size = 0.01
		l.position = af.position + Vector3(0, 3.4, 0)
		add_child(l)
		i += 1
	var cam = Camera3D.new()
	cam.position = Vector3(8, 5.5, 8)
	add_child(cam)
	cam.look_at(Vector3(8, 1.5, -2.5))
	cam.fov = 65
	cam.current = true
