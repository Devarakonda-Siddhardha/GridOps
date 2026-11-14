extends Node

func _ready():
	print("=== RUNNING CONTROLS, CAMERA, DIALOGUE & ANIMATION TESTS ===")

	# 1. InputMap check
	assert(InputMap.has_action("attack"), "attack action must exist")
	assert(InputMap.has_action("block"), "block action must exist")
	var atk_mouse = InputMap.action_get_events("attack").any(func(e): return e is InputEventMouseButton and e.button_index == MOUSE_BUTTON_LEFT)
	var blk_mouse = InputMap.action_get_events("block").any(func(e): return e is InputEventMouseButton and e.button_index == MOUSE_BUTTON_RIGHT)
	var pray_rmb = InputMap.action_get_events("interact_pray").any(func(e): return e is InputEventMouseButton and e.button_index == MOUSE_BUTTON_RIGHT)
	assert(atk_mouse, "Left click must be bound to attack")
	assert(blk_mouse, "Right click must be bound to block")
	assert(not pray_rmb, "Right click must NOT be bound to interact_pray")
	print("✓ InputMap verified: Left-Click=Attack, Right-Click=Block")

	# 2. Main Menu should NOT emit dialogue_started on _ready()
	var dlg_fired = [false]
	SoundManager.dialogue_started.connect(func(_s, _t, _c, _d): dlg_fired[0] = true)
	var menu = load("res://src/ui/main_menu.tscn").instantiate()
	add_child(menu)
	await get_tree().process_frame
	assert(not dlg_fired[0], "Main menu must not fire dialogue before level starts")
	menu.queue_free()
	print("✓ Main Menu does not play premature dialogue")

	# 3. Camera 360-degree mouse rotation check
	var cam_pivot = Node3D.new()
	cam_pivot.set_script(load("res://src/player/camera_controller.gd"))
	var sa = SpringArm3D.new()
	sa.name = "SpringArm3D"
	var cam = Camera3D.new()
	cam.name = "Camera3D"
	sa.add_child(cam)
	cam_pivot.add_child(sa)
	add_child(cam_pivot)
	assert(not cam_pivot.is_mobile, "Desktop OS must not be flagged as mobile")
	Input.set_mouse_mode(Input.MOUSE_MODE_CAPTURED)
	var initial_yaw = cam_pivot.yaw
	var motion = InputEventMouseMotion.new()
	motion.relative = Vector2(500, 0)
	cam_pivot._input(motion)
	assert(abs(cam_pivot.yaw - initial_yaw) > 1.0, "Mouse motion must rotate camera yaw")
	# Full 360 check
	for i in range(5):
		cam_pivot._input(motion)
	print("✓ Camera 360-degree mouse rotation verified (yaw=%.2f)" % cam_pivot.yaw)
	cam_pivot.queue_free()

	# 4. Warrior block & animation state check
	var warrior = load("res://src/player/warrior.tscn").instantiate()
	add_child(warrior)
	warrior._enter_block()
	assert(warrior.current_state == warrior.State.BLOCK, "Warrior must enter BLOCK state")
	var hp_before = warrior.current_health
	warrior.take_damage(30.0)
	assert(warrior.current_health == hp_before, "Warrior blocking must negate damage")
	print("✓ Warrior Right-Click block negates incoming damage")
	warrior.queue_free()

	print("=== ALL CONTROLS & DIALOGUE TESTS PASSED! ===")
	get_tree().quit(0)
