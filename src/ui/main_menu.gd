extends Control

@onready var bg_texture = $Background
@onready var chapter_modal = $ChapterModal
@onready var chapter_list_container = $ChapterModal/Panel/VBox/Scroll/ChapterList
@onready var settings_modal = $SettingsModal
@onready var codex_modal = $CodexModal

# Settings Controls
@onready var master_slider = $SettingsModal/Panel/VBox/Scroll/VBox/MasterRow/Slider
@onready var athena_slider = $SettingsModal/Panel/VBox/Scroll/VBox/AthenaRow/Slider
@onready var sfx_slider = $SettingsModal/Panel/VBox/Scroll/VBox/SfxRow/Slider
@onready var music_slider = $SettingsModal/Panel/VBox/Scroll/VBox/MusicRow/Slider
@onready var fullscreen_btn = $SettingsModal/Panel/VBox/Scroll/VBox/DisplayRow/FullscreenBtn
@onready var touch_toggle_btn = $SettingsModal/Panel/VBox/Scroll/VBox/TouchRow/TouchToggleBtn

const CHAPTERS = [
	{
		"num": 1,
		"title": "Sanctuary of Olympus",
		"location": "Mount Olympus, Greece",
		"desc": "Cleanse the sacred plaza of Mount Olympus and commune at the high altars of Zeus, Poseidon, Hades, and Ares.",
		"boss": "Tartarus Vanguard Fiends",
		"scene": "res://src/levels/level1_sanctuary.tscn"
	},
	{
		"num": 2,
		"title": "Coast of Nauplia",
		"location": "Argolic Gulf Shoreline",
		"desc": "Roman triremes have beached along the Peloponnese coastline. Burn their landing beachhead and break the vanguard.",
		"boss": "Decurion Beachmaster",
		"scene": "res://src/levels/level2_coast.tscn"
	},
	{
		"num": 3,
		"title": "Valley of Arcadia",
		"location": "Peloponnese Pine Forest",
		"desc": "Roman patrols hold captured Spartan soldiers in iron cages. Free your brothers to build the Greek Phalanx army.",
		"boss": "Centurion Slaver",
		"scene": "res://src/levels/level3_valley.tscn"
	},
	{
		"num": 4,
		"title": "Chasm of Tartarus",
		"location": "Underworld Rift",
		"desc": "A catastrophic tear into the Underworld has opened. Dodge seismic ground-slams and vanquish the Infernal Minotaur.",
		"boss": "Infernal Minotaur",
		"scene": "res://src/levels/level4_chasm.tscn"
	},
	{
		"num": 5,
		"title": "Fortress of Corinth",
		"location": "Castrum Roma Citadel",
		"desc": "Assault the fortified Roman garrison. Smash the heavy oak gates, destroy legionary cohorts, and confront Legatus Marcus.",
		"boss": "Legatus Marcus Aurelius",
		"scene": "res://src/levels/level5_siege.tscn"
	},
	{
		"num": 6,
		"title": "Pass of Thermopylae",
		"location": "The Hot Gates",
		"desc": "Stand where King Leonidas stood. Lock shields in Phalanx Shield Wall formation across the narrow pass to repel Roman legions.",
		"boss": "Legionary Cohort Vanguards",
		"scene": "res://src/levels/level6_thermopylae.tscn"
	},
	{
		"num": 7,
		"title": "Oracle of Delphi",
		"location": "Mount Parnassus Sanctuary",
		"desc": "Roman pillagers have desecrated the temple of Apollo. Purge the invaders and claim the divine Golden Aegis.",
		"boss": "Praetor Defiler",
		"scene": "res://src/levels/level7_delphi.tscn"
	},
	{
		"num": 8,
		"title": "Isle of Delos",
		"location": "Cyclades Archipelago",
		"desc": "Liberate captured Cretan toxotes (archers) and Thessalian cavalry. Seize the Roman fleet to take the war to Italy.",
		"boss": "Naval Prefect Valerius",
		"scene": "res://src/levels/level8_delos.tscn"
	},
	{
		"num": 9,
		"title": "The Appian Way",
		"location": "Via Appia, Italy",
		"desc": "The invasion of Italy begins! Charge through Roman encampments, avoid heavy ballistas and catapult fire along the road to Rome.",
		"boss": "Siege Commander Drusus",
		"scene": "res://src/levels/level9_appian_way.tscn"
	},
	{
		"num": 10,
		"title": "The Colosseum of Rome",
		"location": "Imperial Rome",
		"desc": "The ultimate campaign climax. Confront Supreme Consul Titus Claudius and his elite imperial Praetorians in the sands of the Colosseum!",
		"boss": "Supreme Consul Titus Claudius",
		"scene": "res://src/levels/level10_rome_colosseum.tscn"
	}
]

func _ready():
	Input.set_mouse_mode(Input.MOUSE_MODE_VISIBLE)
	chapter_modal.visible = false
	settings_modal.visible = false
	codex_modal.visible = false

	_setup_background()
	_setup_chapter_list()
	_setup_settings_values()

	# Start menu background soundtrack
	if SoundManager:
		SoundManager.play_dialogue("warrior_intro", true)
		get_tree().create_timer(3.0).timeout.connect(func():
			if is_instance_valid(self):
				SoundManager.play_athena("athena_intro", true)
		)

func _setup_background():
	if bg_texture:
		var tex_path = "res://assets/main_menu_bg.jpg"
		if ResourceLoader.exists(tex_path):
			bg_texture.texture = load(tex_path)

func _on_play_pressed():
	_play_click_sfx()
	var lvl = CampaignManager.current_level if CampaignManager.current_level >= 1 else 1
	CampaignManager.load_level(lvl)

func _on_chapter_select_pressed():
	_play_click_sfx()
	chapter_modal.visible = true

func _on_settings_pressed():
	_play_click_sfx()
	settings_modal.visible = true

func _on_codex_pressed():
	_play_click_sfx()
	codex_modal.visible = true

func _on_quit_pressed():
	_play_click_sfx()
	get_tree().quit()

func _setup_chapter_list():
	for child in chapter_list_container.get_children():
		child.queue_free()

	for info in CHAPTERS:
		var card = PanelContainer.new()
		card.custom_minimum_size = Vector2(860, 95)
		var style = StyleBoxFlat.new()
		style.bg_color = Color(0.08, 0.09, 0.14, 0.88)
		style.border_color = Color(0.85, 0.72, 0.28, 0.8)
		style.set_border_width_all(2)
		style.set_corner_radius_all(8)
		card.add_theme_stylebox_override("panel", style)

		var margin = MarginContainer.new()
		margin.add_theme_constant_override("margin_left", 16)
		margin.add_theme_constant_override("margin_right", 16)
		margin.add_theme_constant_override("margin_top", 12)
		margin.add_theme_constant_override("margin_bottom", 12)
		card.add_child(margin)

		var hbox = HBoxContainer.new()
		hbox.add_theme_constant_override("separation", 16)
		margin.add_child(hbox)

		# Chapter Badge
		var badge = Label.new()
		badge.text = "CH %d" % info["num"]
		badge.custom_minimum_size = Vector2(70, 0)
		badge.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		badge.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
		badge.add_theme_font_size_override("font_size", 20)
		badge.add_theme_color_override("font_color", Color(1.0, 0.85, 0.3))
		hbox.add_child(badge)

		# Info VBox
		var info_vbox = VBoxContainer.new()
		info_vbox.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		info_vbox.add_theme_constant_override("separation", 4)
		hbox.add_child(info_vbox)

		var title_lbl = Label.new()
		title_lbl.text = "⚔ " + info["title"] + " — " + info["location"]
		title_lbl.add_theme_font_size_override("font_size", 16)
		title_lbl.add_theme_color_override("font_color", Color(1.0, 0.95, 0.8))
		info_vbox.add_child(title_lbl)

		var desc_lbl = Label.new()
		desc_lbl.text = info["desc"]
		desc_lbl.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
		desc_lbl.add_theme_font_size_override("font_size", 12)
		desc_lbl.add_theme_color_override("font_color", Color(0.8, 0.82, 0.9))
		info_vbox.add_child(desc_lbl)

		var boss_lbl = Label.new()
		boss_lbl.text = "👑 Key Encounter: %s" % info["boss"]
		boss_lbl.add_theme_font_size_override("font_size", 11)
		boss_lbl.add_theme_color_override("font_color", Color(0.9, 0.45, 0.45))
		info_vbox.add_child(boss_lbl)

		# Launch Button
		var btn = Button.new()
		btn.text = "⚔ DEPLOY"
		btn.custom_minimum_size = Vector2(130, 48)
		btn.size_flags_vertical = Control.SIZE_SHRINK_CENTER
		var b_style = StyleBoxFlat.new()
		b_style.bg_color = Color(0.85, 0.65, 0.15, 0.95)
		b_style.border_color = Color(1.0, 0.9, 0.6)
		b_style.set_border_width_all(2)
		b_style.set_corner_radius_all(6)
		btn.add_theme_stylebox_override("normal", b_style)
		btn.add_theme_color_override("font_color", Color(0.08, 0.08, 0.1))
		btn.add_theme_font_size_override("font_size", 15)

		var target_lvl = info["num"]
		btn.pressed.connect(func():
			_play_click_sfx()
			CampaignManager.load_level(target_lvl)
		)
		hbox.add_child(btn)

		chapter_list_container.add_child(card)

func _setup_settings_values():
	# Default slider values
	master_slider.value = 85.0
	athena_slider.value = 100.0
	sfx_slider.value = 85.0
	music_slider.value = 75.0

	master_slider.value_changed.connect(func(val):
		var db = linear_to_db(val / 100.0)
		AudioServer.set_bus_volume_db(0, db)
	)

	athena_slider.value_changed.connect(func(val):
		if SoundManager and SoundManager.athena_player:
			SoundManager.athena_player.volume_db = linear_to_db(val / 100.0) + 5.5
	)

	sfx_slider.value_changed.connect(func(val):
		if SoundManager:
			for p in SoundManager.players:
				p.volume_db = linear_to_db(val / 100.0)
	)

	music_slider.value_changed.connect(func(val):
		if SoundManager and SoundManager.music_player:
			SoundManager.music_player.volume_db = linear_to_db(val / 100.0) - 6.0
	)

	fullscreen_btn.pressed.connect(func():
		_play_click_sfx()
		var mode = DisplayServer.window_get_mode()
		if mode == DisplayServer.WINDOW_MODE_FULLSCREEN:
			DisplayServer.window_set_mode(DisplayServer.WINDOW_MODE_WINDOWED)
			fullscreen_btn.text = "WINDOWED"
		else:
			DisplayServer.window_set_mode(DisplayServer.WINDOW_MODE_FULLSCREEN)
			fullscreen_btn.text = "FULLSCREEN"
	)

	touch_toggle_btn.pressed.connect(func():
		_play_click_sfx()
		var hud = get_tree().get_first_node_in_group("hud")
		if hud and "touch_layer" in hud and hud.touch_layer:
			hud.touch_layer.visible = not hud.touch_layer.visible
			touch_toggle_btn.text = "ON" if hud.touch_layer.visible else "OFF"
		else:
			touch_toggle_btn.text = "TOGGLED"
	)

func _play_click_sfx():
	if SoundManager:
		SoundManager.play("sword_swing", 1.5, -6.0)

func _on_close_modal_pressed():
	_play_click_sfx()
	chapter_modal.visible = false
	settings_modal.visible = false
	codex_modal.visible = false
