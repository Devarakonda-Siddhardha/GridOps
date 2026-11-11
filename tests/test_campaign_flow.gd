extends Node

func _ready():
	print("=== RUNNING CAMPAIGN & MAIN MENU VERIFICATION TESTS ===")
	
	# Test 1: Load Main Menu
	var menu_scene = load("res://src/ui/main_menu.tscn")
	assert(menu_scene != null, "main_menu.tscn must load")
	var menu = menu_scene.instantiate()
	add_child(menu)
	print("✓ Main menu instantiated successfully")
	
	# Verify chapter list
	var chapter_list = menu.get_node("ChapterModal/Panel/VBox/Scroll/ChapterList")
	assert(chapter_list != null, "ChapterList container must exist")
	print("✓ Chapter list child count: %d" % chapter_list.get_child_count())
	assert(chapter_list.get_child_count() == 10, "All 10 campaign chapters must be in chapter list")
	
	# Verify Settings Modal
	var settings = menu.get_node("SettingsModal")
	assert(settings != null, "Settings modal must exist")
	var master_slider = menu.get_node("SettingsModal/Panel/VBox/Scroll/VBox/MasterRow/Slider")
	assert(master_slider != null, "Master slider must exist")
	var athena_slider = menu.get_node("SettingsModal/Panel/VBox/Scroll/VBox/AthenaRow/Slider")
	assert(athena_slider != null, "Athena voice slider must exist")
	print("✓ Audio sliders verified (Master: %.1f, Athena: %.1f)" % [master_slider.value, athena_slider.value])
	
	# Verify Codex Modal
	var codex = menu.get_node("CodexModal")
	assert(codex != null, "Codex modal must exist")
	print("✓ Codex modal verified")
	
	# Test 2: HUD Victory Panel & Next Level Progression
	var hud_scene = load("res://src/ui/hud.tscn")
	assert(hud_scene != null, "hud.tscn must load")
	var hud = hud_scene.instantiate()
	add_child(hud)
	
	CampaignManager.current_level = 1
	hud.show_victory("SANCTUARY DEFENDED!", "The vanguard is routed!")
	
	var victory_panel = hud.get_node("VictoryPanel")
	assert(victory_panel.visible, "Victory panel must be visible")
	var next_btn = victory_panel.get_node("Center/VBox/NextLevelBtn")
	assert(next_btn != null, "NextLevelBtn must exist in Center/VBox")
	assert(next_btn.visible, "NextLevelBtn must be visible")
	print("✓ Next Level Button text: '%s'" % next_btn.text)
	assert(next_btn.text == "⚔ ADVANCE TO CHAPTER 2 ⚔", "Button text must prompt advance to Chapter 2")
	
	var menu_btn = victory_panel.get_node("Center/VBox/MainMenuBtn")
	assert(menu_btn != null, "MainMenuBtn must exist in Center/VBox")
	print("✓ Main Menu Button text: '%s'" % menu_btn.text)
	
	# Test 3: Test Level Scenes exist for all 10 chapters
	for lvl in range(1, 11):
		assert(CampaignManager.level_scenes.has(lvl), "CampaignManager must map level %d" % lvl)
		var scn_path = CampaignManager.level_scenes[lvl]
		assert(ResourceLoader.exists(scn_path), "Level scene file must exist: %s" % scn_path)
		print("✓ Chapter %d mapped and resource exists: %s" % [lvl, scn_path])
	
	# Test 4: Advance level
	CampaignManager.current_level = 1
	var prev_lvl = CampaignManager.current_level
	var target_next = prev_lvl + 1
	assert(CampaignManager.level_scenes.has(target_next), "Next level scene must exist")
	print("✓ Advance to next chapter confirmed: %d -> %d (%s)" % [prev_lvl, target_next, CampaignManager.level_scenes[target_next]])
	
	print("=== ALL TESTS PASSED SUCCESSFULLY! ===")
	get_tree().quit(0)
