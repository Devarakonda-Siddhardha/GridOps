extends SceneTree

func _init():
	for f in ["warrior.glb", "archer.glb", "cavalry.glb", "demon.glb", "greek_soldier.glb", "roman_soldier.glb"]:
		var s = load("res://assets/models/" + f)
		if s:
			var inst = s.instantiate()
			var ap = inst.get_node_or_null("AnimationPlayer")
			if ap:
				print(f, " -> ", ap.get_animation_list())
			else:
				print(f, " -> NO AnimationPlayer")
	quit()
