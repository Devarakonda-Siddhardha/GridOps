extends Node

# usage: godot --path . res://tests/shot.tscn -- <scene> <out.png> [cam_height]
func _ready():
	var args = OS.get_cmdline_user_args()
	var scene_path = args[0]
	var out = args[1]
	var inst = load(scene_path).instantiate()
	get_tree().root.add_child.call_deferred(inst)
	await get_tree().create_timer(3.5).timeout
	if args.size() > 2 and args[2] == "nohud":
		var h = inst.get_node_or_null("HUD")
		if h: h.visible = false
		await get_tree().process_frame
		await get_tree().process_frame
	var img = get_viewport().get_texture().get_image()
	img.save_png(out)
	print("saved ", out, " ", img.get_size())
	get_tree().quit()
