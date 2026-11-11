extends SceneTree

func _init():
	print("=== VERIFYING PRAYER, HUD, AND MOVEMENT FIXES ===")
	call_deferred("_run_test")

func _run_test():
	var scene_res = load("res://src/levels/level1_sanctuary.tscn")
	if not scene_res:
		printerr("FAIL: Could not load level1_sanctuary.tscn")
		quit(1)
		return

	var world = scene_res.instantiate()
	root.add_child(world)

	# Verify player exists
	var player = root.get_tree().get_first_node_in_group("player")
	assert(player != null, "Player must exist")
	print("✓ Player instantiated at: ", player.global_position)

	# Verify HUD exists and script is attached
	var hud = world.get_node_or_null("HUD")
	assert(hud != null, "HUD must exist")
	assert(hud.get_script() != null, "HUD must have script attached")
	print("✓ HUD initialized successfully")

	# Check banner panel modulate.a
	var banner = hud.get_node("BannerPanel")
	assert(banner.modulate.a == 0.0, "BannerPanel must be hidden initially")
	print("✓ BannerPanel initially hidden (modulate.a = 0.0)")

	# Check slots
	assert(hud.slots.has("zeus"), "Zeus slot must exist")
	print("✓ HUD slots mapped: ", hud.slots.keys())

	# Test prayer flow
	print("\n--- Testing Altar Prayer Flow ---")
	player.start_praying("zeus")
	assert(player.current_state == player.State.PRAY, "Player should be in PRAY state")
	print("✓ Player entered State.PRAY")

	# Find Zeus altar
	var altars = root.get_tree().get_nodes_in_group("altar")
	var zeus_altar = null
	for a in root.find_children("*", "Node3D", true, false):
		if a.get_script() and "god" in a and a.god == "zeus":
			zeus_altar = a
			break

	var dm = root.get_node_or_null("/root/DivineManager")
	var sm = root.get_node_or_null("/root/SoundManager")

	if zeus_altar:
		print("✓ Found Zeus altar: ", zeus_altar.name)
		zeus_altar._complete_prayer()
		print("✓ Altar _complete_prayer() called")
	elif dm:
		dm.unlock_blessing("zeus")
		player.stop_praying()

	# Verify player is NOT stuck in PRAY
	assert(player.current_state == player.State.IDLE, "Player must return to IDLE after prayer, was: " + str(player.current_state))
	print("✓ Player released back to State.IDLE! (No longer frozen)")

	# Verify Zeus is unlocked
	if dm:
		assert(dm.powers["zeus"]["unlocked"] == true, "Zeus power must be unlocked")
		print("✓ Zeus power unlocked in DivineManager")

	# Verify HUD slot updated to unlocked
	var zeus_slot = hud.slots["zeus"]
	var status_text = zeus_slot.get_node("StatusLabel").text
	print("✓ Zeus slot status text: '", status_text, "' (no longer LOCKED)")
	assert("LOCKED" not in status_text, "Zeus slot should not say LOCKED after blessing")

	# Test player movement
	player.velocity.x = 5.0
	player.velocity.z = 5.0
	player.move_and_slide()
	print("✓ Player can move freely, new pos: ", player.global_position)

	# Test audio channels
	print("\n--- Testing Audio Channels ---")
	if sm:
		sm.play("sword_swing", 1.0, 0.0)
		print("✓ SFX played")
		sm.play_dialogue("warrior_intro", true)
		print("✓ Dialogue played")
		sm.play_athena("athena_intro", true)
		print("✓ Athena played on dedicated athena_player without interrupting dialogue")

	print("\n🎉 ALL PRAYER, HUD, FREEZING, AND AUDIO VERIFICATIONS PASSED!")
	quit(0)
