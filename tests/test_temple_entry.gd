extends SceneTree

# Headless physics verification test for temple entrance ramps and Athena placement

func _init():
	print("\n=== STARTING TEMPLE ENTRY PHYSICS VERIFICATION ===")
	call_deferred("_run_tests")

func _run_tests():
	var root_node = Node3D.new()
	root.add_child(root_node)
	
	# Load TempleArena
	var arena_packed = load("res://src/environment/temple_arena.tscn")
	if not arena_packed:
		printerr("FAIL: Could not load temple_arena.tscn")
		quit(1)
		return
	var arena = arena_packed.instantiate()
	root_node.add_child(arena)
	
	# Load Warrior
	var warrior_packed = load("res://src/player/warrior.tscn")
	if not warrior_packed:
		printerr("FAIL: Could not load warrior.tscn")
		quit(1)
		return
	
	# Test paths into all 4 temples
	var tests = [
		{
			"name": "Zeus Temple (North)",
			"start": Vector3(0, 0.1, -20),
			"target": Vector3(0, 0.1, -40),
			"expected_min_y": 0.85,
			"target_coord": "z",
			"target_threshold": -36.0,
			"should_be_less": true
		},
		{
			"name": "Hades Temple (South)",
			"start": Vector3(0, 0.1, 20),
			"target": Vector3(0, 0.1, 40),
			"expected_min_y": 0.85,
			"target_coord": "z",
			"target_threshold": 36.0,
			"should_be_less": false
		},
		{
			"name": "Poseidon Temple (West)",
			"start": Vector3(-20, 0.1, 0),
			"target": Vector3(-40, 0.1, 0),
			"expected_min_y": 0.85,
			"target_coord": "x",
			"target_threshold": -36.0,
			"should_be_less": true
		},
		{
			"name": "Ares Temple (East)",
			"start": Vector3(20, 0.1, 0),
			"target": Vector3(40, 0.1, 0),
			"expected_min_y": 0.85,
			"target_coord": "x",
			"target_threshold": 36.0,
			"should_be_less": false
		}
	]
	
	var all_passed = true
	
	for t in tests:
		print("\n--- Testing Entrance to: %s ---" % t.name)
		var player: CharacterBody3D = warrior_packed.instantiate()
		root_node.add_child(player)
		player.global_position = t.start
		
		var dir = (t.target - t.start).normalized()
		var speed = 7.0
		var dt = 1.0 / 60.0
		var steps = 240 # 4 seconds of walking
		
		for s in range(steps):
			player.velocity.x = dir.x * speed
			player.velocity.z = dir.z * speed
			player.velocity.y = -9.8 * dt # Gravity
			player.move_and_slide()
		
		var final_pos = player.global_position
		print("  Final Position: %s" % str(final_pos))
		print("  Final Floor Y: %.3f (Expected >= %.2f)" % [final_pos.y, t.expected_min_y])
		var col_count = player.get_slide_collision_count()
		print("  Collision count at stop: %d" % col_count)
		for ci in range(col_count):
			var col = player.get_slide_collision(ci)
			print("    Col %d: collider=%s, normal=%s, pos=%s" % [ci, col.get_collider().name, str(col.get_normal()), str(col.get_position())])
			var shape_owner = col.get_collider_shape()
			print("    Col %d shape_index=%s" % [ci, str(shape_owner)])
		
		var coord_val = final_pos.z if t.target_coord == "z" else final_pos.x
		var reached_deep = (coord_val <= t.target_threshold) if t.should_be_less else (coord_val >= t.target_threshold)
		var reached_y = final_pos.y >= t.expected_min_y
		
		if reached_deep and reached_y:
			print("  [PASS] Successfully walked up ramp and entered %s cella!" % t.name)
		else:
			print("  [FAIL] Did not enter %s cella! Reached depth: %s (needed %s %f), Y: %f" % [
				t.name, reached_deep, ("<=" if t.should_be_less else ">="), t.target_threshold, final_pos.y
			])
			all_passed = false
			
		player.queue_free()
	
	# Test North Promenade clearance past old Athena spot (0, 0, -12)
	print("\n--- Testing North Promenade clearance through (0, 0, -12) ---")
	var prom_player: CharacterBody3D = warrior_packed.instantiate()
	root_node.add_child(prom_player)
	prom_player.global_position = Vector3(0, 0.1, 0)
	var prom_dir = Vector3(0, 0, -1)
	for s in range(180): # 3 seconds
		prom_player.velocity = prom_dir * 7.0
		prom_player.velocity.y = -9.8 * (1.0 / 60.0)
		prom_player.move_and_slide()
	
	print("  Promenade Walk final pos: %s" % str(prom_player.global_position))
	if prom_player.global_position.z <= -15.0:
		print("  [PASS] North promenade clear! Walked past Z=-12 unimpeded.")
	else:
		print("  [FAIL] Blocked on North promenade at Z = %f" % prom_player.global_position.z)
		all_passed = false
	prom_player.queue_free()
	
	# Test Athena interaction at side terrace (-16, 0, -8)
	print("\n--- Testing Athena Proximity at side terrace (-16, 0, -8) ---")
	var athena_node = arena.get_node_or_null("AthenaSanctuary/GodAthena")
	if athena_node:
		print("  Found GodAthena at: %s" % str(athena_node.global_position))
		var ath_player: CharacterBody3D = warrior_packed.instantiate()
		root_node.add_child(ath_player)
		ath_player.global_position = Vector3(-10, 0.1, -8)
		var to_athena = (athena_node.global_position - ath_player.global_position).normalized()
		for s in range(90):
			ath_player.velocity = to_athena * 5.0
			ath_player.velocity.y = -9.8 * (1.0 / 60.0)
			ath_player.move_and_slide()
		
		var dist_to_athena = ath_player.global_position.distance_to(athena_node.global_position)
		print("  Distance to Athena: %.2fm (ProximityArea radius is 6.5m)" % dist_to_athena)
		if dist_to_athena <= 3.0:
			print("  [PASS] Player can approach Athena closely for communes and blessings!")
		else:
			print("  [FAIL] Player could not approach Athena! Distance: %.2f" % dist_to_athena)
			all_passed = false
		ath_player.queue_free()
	# Test Cavalry (mounted warrior) galloping up ramp into Zeus temple
	print("\n--- Testing Cavalry Galloping Entrance to Zeus Temple ---")
	var cav_packed = load("res://src/player/cavalry.tscn")
	if cav_packed:
		var cav: CharacterBody3D = cav_packed.instantiate()
		root_node.add_child(cav)
		cav.global_position = Vector3(0, 0.1, -20)
		var cav_dir = Vector3(0, 0, -1)
		var cav_speed = 10.0
		for s in range(200):
			cav.velocity = cav_dir * cav_speed
			cav.velocity.y = -9.8 * (1.0 / 60.0)
			cav.move_and_slide()
		print("  Cavalry final pos: %s, Floor Y: %.3f" % [str(cav.global_position), cav.global_position.y])
		var c_count = cav.get_slide_collision_count()
		for ci in range(c_count):
			var c = cav.get_slide_collision(ci)
			print("    Cav col %d: collider=%s, normal=%s, pos=%s" % [ci, c.get_collider().name, str(c.get_normal()), str(c.get_position())])
			print("    Cav shape: %s" % str(c.get_collider_shape()))
		if cav.global_position.z <= -36.0 and cav.global_position.y >= 0.85:
			print("  [PASS] Cavalry mounted unit galloped up ramp and entered temple cella!")
		else:
			print("  [FAIL] Cavalry mounted unit blocked at %s!" % str(cav.global_position))
			all_passed = false
		cav.queue_free()

	print("\n=== SUMMARY ===")
	if all_passed:
		print("ALL PHYSICS TESTS PASSED! Ramps and entry colonnades fully functional.")
		quit(0)
	else:
		printerr("ONE OR MORE TESTS FAILED!")
		quit(1)
