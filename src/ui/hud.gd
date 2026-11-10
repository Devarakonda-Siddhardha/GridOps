extends CanvasLayer

@onready var hp_bar: ProgressBar = $TopLeft/VBox/HpBar
@onready var hp_text: Label = $TopLeft/VBox/HpBar/HpText
@onready var sp_bar: ProgressBar = $TopLeft/VBox/SpBar
@onready var sp_text: Label = $TopLeft/VBox/SpBar/SpText

@onready var wave_label: Label = $TopRight/VBox/WaveLabel
@onready var enemy_count_label: Label = $TopRight/VBox/EnemyCountLabel

@onready var banner_panel: Control = $BannerPanel
@onready var banner_title: Label = $BannerPanel/VBox/BannerTitle
@onready var banner_subtitle: Label = $BannerPanel/VBox/BannerSubtitle

@onready var victory_panel: Control = $VictoryPanel
@onready var game_over_panel: Control = $GameOverPanel

@onready var slot_zeus: Control = $BottomCenter/SkillBar/SlotZeus
@onready var slot_poseidon: Control = $BottomCenter/SkillBar/SlotPoseidon
@onready var slot_hades: Control = $BottomCenter/SkillBar/SlotHades
@onready var slot_ares: Control = $BottomCenter/SkillBar/SlotAres

var slots = {}

var dialogue_container: PanelContainer
var dialogue_speaker_label: Label
var dialogue_text_label: Label
var dialogue_tween: Tween

var army_panel: PanelContainer
var army_count_label: Label
var army_hint_label: Label

var boss_bar_container: PanelContainer
var boss_hp_bar: ProgressBar
var boss_title_label: Label

var next_level_btn: Button
var class_badge_label: Label

func _ready():
	banner_panel.modulate.a = 0.0
	victory_panel.visible = false
	game_over_panel.visible = false

	slots = {
		"zeus": slot_zeus,
		"poseidon": slot_poseidon,
		"hades": slot_hades,
		"ares": slot_ares
	}

	DivineManager.connect("power_unlocked", Callable(self, "_on_power_unlocked"))
	DivineManager.connect("cooldown_updated", Callable(self, "_on_cooldown_updated"))
	DivineManager.connect("message_broadcast", Callable(self, "show_banner"))
	DivineManager.connect("boss_spawned", Callable(self, "_on_boss_spawned"))
	DivineManager.connect("boss_health_updated", Callable(self, "update_boss_hp"))
	DivineManager.connect("boss_defeated", Callable(self, "_on_boss_defeated"))
	SoundManager.connect("dialogue_started", Callable(self, "_on_dialogue_started"))

	CampaignManager.connect("army_changed", Callable(self, "_on_army_changed"))
	CampaignManager.connect("objective_updated", Callable(self, "set_objective"))
	CampaignManager.connect("hero_class_changed", Callable(self, "_on_class_changed"))

	_create_dialogue_ui()
	_create_army_ui()
	_create_class_ui()
	_create_boss_bar_ui()
	_setup_victory_panel()
	_setup_touch_controls()

	var p = get_tree().get_first_node_in_group("player")
	if p:
		setup_player_bindings(p)

	# Initial slot setup
	for god in slots.keys():
		var slot = slots[god]
		var info = DivineManager.powers[god]
		slot.get_node("KeyLabel").text = "[" + info["key"] + "]"
		slot.get_node("NameLabel").text = info["name"]
		slot.get_node("StatusLabel").text = "LOCKED\n(Pray at Altar)" if not info["unlocked"] else info["title"]
		slot.get_node("CooldownOverlay").visible = false
		slot.modulate = Color(1.0, 1.0, 1.0, 1.0) if info["unlocked"] else Color(0.6, 0.6, 0.6, 0.6)
		slot.mouse_filter = Control.MOUSE_FILTER_STOP
		var current_god = god
		slot.gui_input.connect(func(ev):
			if (ev is InputEventMouseButton and ev.pressed and ev.button_index == MOUSE_BUTTON_LEFT) or (ev is InputEventScreenTouch and ev.pressed):
				DivineManager.cast_power(current_god)
		)

func _create_dialogue_ui():
	dialogue_container = PanelContainer.new()
	dialogue_container.name = "DialogueContainer"
	add_child(dialogue_container)

	dialogue_container.set_anchors_preset(Control.PRESET_BOTTOM_WIDE)
	dialogue_container.offset_left = 220
	dialogue_container.offset_right = -220
	dialogue_container.offset_top = -215
	dialogue_container.offset_bottom = -135
	dialogue_container.mouse_filter = Control.MOUSE_FILTER_IGNORE

	var style = StyleBoxFlat.new()
	style.bg_color = Color(0.06, 0.06, 0.1, 0.92)
	style.border_color = Color(0.9, 0.78, 0.28, 0.95)
	style.set_border_width_all(2)
	style.set_corner_radius_all(10)
	style.content_margin_left = 20
	style.content_margin_right = 20
	style.content_margin_top = 10
	style.content_margin_bottom = 10
	dialogue_container.add_theme_stylebox_override("panel", style)

	var vbox = VBoxContainer.new()
	vbox.add_theme_constant_override("separation", 4)
	dialogue_container.add_child(vbox)

	dialogue_speaker_label = Label.new()
	dialogue_speaker_label.add_theme_font_size_override("font_size", 14)
	dialogue_speaker_label.add_theme_color_override("font_outline_color", Color.BLACK)
	dialogue_speaker_label.add_theme_constant_override("outline_size", 3)
	vbox.add_child(dialogue_speaker_label)

	dialogue_text_label = Label.new()
	dialogue_text_label.add_theme_font_size_override("font_size", 14)
	dialogue_text_label.add_theme_color_override("font_color", Color(0.95, 0.95, 0.95))
	dialogue_text_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	vbox.add_child(dialogue_text_label)

	dialogue_container.modulate.a = 0.0

func _create_army_ui():
	army_panel = PanelContainer.new()
	army_panel.name = "ArmyPanel"
	add_child(army_panel)

	army_panel.set_anchors_preset(Control.PRESET_TOP_RIGHT)
	army_panel.offset_left = -340
	army_panel.offset_top = 110
	army_panel.offset_right = -24
	army_panel.offset_bottom = 195

	var style = StyleBoxFlat.new()
	style.bg_color = Color(0.08, 0.12, 0.22, 0.88)
	style.border_color = Color(0.3, 0.65, 1.0, 0.9)
	style.set_border_width_all(2)
	style.set_corner_radius_all(8)
	style.content_margin_left = 14
	style.content_margin_right = 14
	style.content_margin_top = 8
	style.content_margin_bottom = 8
	army_panel.add_theme_stylebox_override("panel", style)

	var vbox = VBoxContainer.new()
	vbox.add_theme_constant_override("separation", 4)
	army_panel.add_child(vbox)

	army_count_label = Label.new()
	army_count_label.text = "🛡️ GREEK PHALANX: 0 / 16"
	army_count_label.add_theme_font_size_override("font_size", 15)
	army_count_label.add_theme_color_override("font_color", Color(0.4, 0.8, 1.0))
	army_count_label.add_theme_color_override("font_outline_color", Color.BLACK)
	army_count_label.add_theme_constant_override("outline_size", 4)
	vbox.add_child(army_count_label)

	army_hint_label = Label.new()
	army_hint_label.text = "[G] Charge  [H] Shield Wall  [V] Rally  |  [B] Codex"
	army_hint_label.add_theme_font_size_override("font_size", 11)
	army_hint_label.add_theme_color_override("font_color", Color(0.85, 0.85, 0.85))
	vbox.add_child(army_hint_label)

	# Instantiate Codex Dialog
	var codex_scene = load("res://src/ui/codex_dialog.tscn")
	if codex_scene:
		var codex_inst = codex_scene.instantiate()
		add_child(codex_inst)

	_on_army_changed(CampaignManager.army_count, CampaignManager.max_army_count)

func _create_class_ui():
	var top_left_vbox = $TopLeft/VBox
	if top_left_vbox:
		class_badge_label = Label.new()
		class_badge_label.name = "ClassBadgeLabel"
		class_badge_label.add_theme_font_size_override("font_size", 13)
		class_badge_label.add_theme_color_override("font_color", Color(1.0, 0.85, 0.3))
		class_badge_label.add_theme_color_override("font_outline_color", Color.BLACK)
		class_badge_label.add_theme_constant_override("outline_size", 4)
		top_left_vbox.add_child(class_badge_label)
		_on_class_changed(CampaignManager.selected_class)

func _on_class_changed(new_class: String):
	if class_badge_label:
		if new_class == "warrior":
			class_badge_label.text = "⚔️ SPARTAN CHAMPION  [TAB: Switch Class]"
			class_badge_label.modulate = Color(1.0, 0.85, 0.3)
		elif new_class == "archer":
			class_badge_label.text = "🏹 CRETAN ARCHER  [TAB: Switch Class]"
			class_badge_label.modulate = Color(0.3, 0.9, 0.5)
		elif new_class == "cavalry":
			class_badge_label.text = "🐎 THESSALIAN CAVALRY  [TAB: Switch Class]"
			class_badge_label.modulate = Color(0.9, 0.65, 0.2)

func setup_player_bindings(player: Node3D):
	if not player:
		return
	if player.has_signal("health_changed"):
		if not player.is_connected("health_changed", Callable(self, "update_hp")):
			player.connect("health_changed", Callable(self, "update_hp"))
	if player.has_signal("stamina_changed"):
		if not player.is_connected("stamina_changed", Callable(self, "update_stamina")):
			player.connect("stamina_changed", Callable(self, "update_stamina"))
	if player.has_signal("died"):
		if not player.is_connected("died", Callable(self, "show_game_over")):
			player.connect("died", Callable(self, "show_game_over"))
	update_hp(player.current_health, player.max_health)
	update_stamina(player.current_stamina, player.max_stamina)
	_on_class_changed(CampaignManager.selected_class)

func _create_boss_bar_ui():
	boss_bar_container = PanelContainer.new()
	boss_bar_container.name = "BossBarContainer"
	add_child(boss_bar_container)

	boss_bar_container.set_anchors_preset(Control.PRESET_CENTER_TOP)
	boss_bar_container.offset_left = -260
	boss_bar_container.offset_right = 260
	boss_bar_container.offset_top = 24
	boss_bar_container.offset_bottom = 84
	boss_bar_container.visible = false

	var style = StyleBoxFlat.new()
	style.bg_color = Color(0.12, 0.05, 0.16, 0.92)
	style.border_color = Color(0.85, 0.25, 0.95, 0.9)
	style.set_border_width_all(2)
	style.set_corner_radius_all(8)
	style.content_margin_left = 16
	style.content_margin_right = 16
	style.content_margin_top = 6
	style.content_margin_bottom = 6
	boss_bar_container.add_theme_stylebox_override("panel", style)

	var vbox = VBoxContainer.new()
	vbox.add_theme_constant_override("separation", 4)
	boss_bar_container.add_child(vbox)

	boss_title_label = Label.new()
	boss_title_label.text = "👑 GENERAL MARCUS AURELIUS - LEGATUS OF ROME"
	boss_title_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	boss_title_label.add_theme_font_size_override("font_size", 13)
	boss_title_label.add_theme_color_override("font_color", Color(1.0, 0.85, 0.3))
	boss_title_label.add_theme_color_override("font_outline_color", Color.BLACK)
	boss_title_label.add_theme_constant_override("outline_size", 4)
	vbox.add_child(boss_title_label)

	boss_hp_bar = ProgressBar.new()
	boss_hp_bar.custom_minimum_size = Vector2(480, 20)
	boss_hp_bar.max_value = 850.0
	boss_hp_bar.value = 850.0
	boss_hp_bar.show_percentage = true

	var fill_style = StyleBoxFlat.new()
	fill_style.bg_color = Color(0.85, 0.15, 0.65)
	fill_style.set_corner_radius_all(6)
	boss_hp_bar.add_theme_stylebox_override("fill", fill_style)

	var bg_style = StyleBoxFlat.new()
	bg_style.bg_color = Color(0.2, 0.08, 0.25)
	bg_style.set_corner_radius_all(6)
	boss_hp_bar.add_theme_stylebox_override("background", bg_style)
	vbox.add_child(boss_hp_bar)

func _setup_victory_panel():
	var btn_vbox = victory_panel.get_node_or_null("VBox")
	if btn_vbox and not btn_vbox.has_node("NextLevelBtn"):
		next_level_btn = Button.new()
		next_level_btn.name = "NextLevelBtn"
		next_level_btn.text = "⚔ ADVANCE TO NEXT CHAPTER ⚔"
		next_level_btn.custom_minimum_size = Vector2(280, 48)
		next_level_btn.add_theme_font_size_override("font_size", 16)
		next_level_btn.connect("pressed", Callable(self, "_on_next_level_pressed"))
		btn_vbox.add_child(next_level_btn)
		btn_vbox.move_child(next_level_btn, 0)

func _on_boss_spawned(boss_name: String, max_hp: float):
	if boss_bar_container:
		boss_bar_container.visible = true
		boss_bar_container.modulate.a = 1.0
	if boss_title_label:
		boss_title_label.text = "👑 " + boss_name
	if boss_hp_bar:
		boss_hp_bar.max_value = max_hp
		boss_hp_bar.value = max_hp

func _on_boss_defeated():
	if boss_bar_container:
		var tw = create_tween()
		tw.tween_property(boss_bar_container, "modulate:a", 0.0, 1.0)
		tw.tween_callback(func(): boss_bar_container.visible = false)

func update_boss_hp(current: float, max_val: float):
	if boss_bar_container:
		boss_bar_container.visible = true
	if boss_hp_bar:
		boss_hp_bar.max_value = max_val
		boss_hp_bar.value = current

func _on_army_changed(count: int, max_count: int):
	if army_count_label:
		army_count_label.text = "🛡️ GREEK PHALANX: %d / %d" % [count, max_count]
		if count > 0:
			army_count_label.modulate = Color(0.4, 0.85, 1.0)
		else:
			army_count_label.modulate = Color(0.7, 0.7, 0.7)

func set_objective(obj_text: String):
	if enemy_count_label:
		enemy_count_label.text = obj_text

func _on_next_level_pressed():
	CampaignManager.advance_to_next_level()

func _on_dialogue_started(speaker: String, text: String, color: Color, duration: float):
	if not dialogue_container:
		return
	dialogue_speaker_label.text = "✦ " + speaker.to_upper()
	dialogue_speaker_label.add_theme_color_override("font_color", color)
	dialogue_text_label.text = '"' + text + '"'

	if dialogue_tween and dialogue_tween.is_valid():
		dialogue_tween.kill()

	dialogue_tween = create_tween()
	dialogue_tween.tween_property(dialogue_container, "modulate:a", 1.0, 0.2)
	dialogue_tween.tween_interval(duration)
	dialogue_tween.tween_property(dialogue_container, "modulate:a", 0.0, 0.4)

func update_hp(current: float, max_val: float):
	if hp_bar:
		hp_bar.max_value = max_val
		hp_bar.value = current
	if hp_text:
		hp_text.text = "%d / %d HP" % [int(current), int(max_val)]
	if AthenaCommentary:
		AthenaCommentary.check_player_health(current, max_val)

func update_stamina(current: float, max_val: float):
	if sp_bar:
		sp_bar.max_value = max_val
		sp_bar.value = current
	if sp_text:
		sp_text.text = "%d / %d SP" % [int(current), int(max_val)]

func update_wave_info(wave_num: int, total_enemies: int):
	if wave_label:
		wave_label.text = "CHAPTER %d" % CampaignManager.current_level
	if enemy_count_label:
		enemy_count_label.text = "%d Enemies Remaining" % total_enemies

func update_enemies_remaining(remaining: int, total_enemies: int):
	if enemy_count_label:
		enemy_count_label.text = "%d / %d Enemies Remaining" % [remaining, total_enemies]

func _on_power_unlocked(god: String):
	if slots.has(god):
		var slot = slots[god]
		var info = DivineManager.powers[god]
		slot.modulate = Color(1.0, 1.0, 1.0, 1.0)
		slot.get_node("StatusLabel").text = info["title"]
		slot.get_node("StatusLabel").modulate = info["color"]

func _on_cooldown_updated(god: String, remaining: float, max_cd: float):
	if slots.has(god):
		var slot = slots[god]
		var overlay = slot.get_node("CooldownOverlay")
		var cd_label = slot.get_node("CooldownOverlay/CdLabel")
		if remaining > 0.05:
			overlay.visible = true
			cd_label.text = "%.1fs" % remaining
		else:
			overlay.visible = false

func show_banner(title: String, subtitle: String):
	banner_title.text = title
	banner_subtitle.text = subtitle

	var tween = create_tween()
	tween.tween_property(banner_panel, "modulate:a", 1.0, 0.3)
	tween.tween_interval(2.6)
	tween.tween_property(banner_panel, "modulate:a", 0.0, 0.5)

func show_victory(custom_title: String = "VICTORY ACHIEVED!", custom_sub: String = "The Roman Cohort has been routed!"):
	var v_title = victory_panel.get_node_or_null("VBox/Title")
	if v_title:
		v_title.text = custom_title
	var v_sub = victory_panel.get_node_or_null("VBox/Subtitle")
	if v_sub:
		v_sub.text = custom_sub
	victory_panel.visible = true
	Input.set_mouse_mode(Input.MOUSE_MODE_VISIBLE)

func show_game_over():
	game_over_panel.visible = true
	Input.set_mouse_mode(Input.MOUSE_MODE_VISIBLE)

func _on_restart_pressed():
	get_tree().reload_current_scene()

var touch_layer: Control = null

func _setup_touch_controls():
	touch_layer = Control.new()
	touch_layer.name = "TouchControls"
	touch_layer.set_anchors_preset(Control.PRESET_FULL_RECT)
	touch_layer.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(touch_layer)

	var is_touch_device = OS.get_name() == "Android" or DisplayServer.is_touchscreen_available()
	touch_layer.visible = is_touch_device

	# Toggle touch button in top-right
	var toggle_btn = Button.new()
	toggle_btn.text = "📱 TOUCH"
	toggle_btn.tooltip_text = "Toggle On-Screen Touch Controls"
	toggle_btn.set_anchors_preset(Control.PRESET_TOP_RIGHT)
	toggle_btn.offset_left = -110
	toggle_btn.offset_top = 16
	toggle_btn.offset_right = -20
	toggle_btn.offset_bottom = 44
	toggle_btn.focus_mode = Control.FOCUS_NONE
	var t_style = StyleBoxFlat.new()
	t_style.bg_color = Color(0.12, 0.12, 0.18, 0.85)
	t_style.border_color = Color(0.9, 0.8, 0.3, 0.8)
	t_style.set_border_width_all(1)
	t_style.set_corner_radius_all(6)
	toggle_btn.add_theme_stylebox_override("normal", t_style)
	toggle_btn.pressed.connect(func():
		touch_layer.visible = not touch_layer.visible
	)
	add_child(toggle_btn)

	# --- Virtual D-Pad / Movement (Bottom-Left) ---
	var dpad = Control.new()
	dpad.name = "DPad"
	dpad.set_anchors_preset(Control.PRESET_BOTTOM_LEFT)
	dpad.offset_left = 30
	dpad.offset_top = -220
	dpad.offset_right = 210
	dpad.offset_bottom = -40
	dpad.mouse_filter = Control.MOUSE_FILTER_IGNORE
	touch_layer.add_child(dpad)

	_create_touch_btn(dpad, "▲", Vector2(60, 0), Vector2(60, 55), "move_forward")
	_create_touch_btn(dpad, "▼", Vector2(60, 120), Vector2(60, 55), "move_backward")
	_create_touch_btn(dpad, "◀", Vector2(0, 60), Vector2(55, 60), "move_left")
	_create_touch_btn(dpad, "▶", Vector2(125, 60), Vector2(55, 60), "move_right")

	# Center Greek Pillar / Crest emblem
	var center_icon = Label.new()
	center_icon.text = "🏛️"
	center_icon.position = Vector2(72, 70)
	center_icon.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	center_icon.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	center_icon.theme_override_font_sizes/font_size = 24
	center_icon.mouse_filter = Control.MOUSE_FILTER_IGNORE
	dpad.add_child(center_icon)

	# --- Action Buttons Cluster (Bottom-Right) ---
	var actions = Control.new()
	actions.name = "ActionButtons"
	actions.set_anchors_preset(Control.PRESET_BOTTOM_RIGHT)
	actions.offset_left = -260
	actions.offset_top = -240
	actions.offset_right = -20
	actions.offset_bottom = -20
	actions.mouse_filter = Control.MOUSE_FILTER_IGNORE
	touch_layer.add_child(actions)

	# ⚔ Attack button (Primary, large)
	var atk_btn = _create_action_btn(actions, "⚔\nATTACK", Vector2(140, 120), Vector2(90, 90), Color(0.85, 0.2, 0.2, 0.85))
	atk_btn.button_down.connect(func(): Input.action_press("attack"))
	atk_btn.button_up.connect(func(): Input.action_release("attack"))

	# 🦘 Jump button
	var jmp_btn = _create_action_btn(actions, "🦘\nJUMP", Vector2(50, 140), Vector2(70, 70), Color(0.2, 0.6, 0.9, 0.85))
	jmp_btn.button_down.connect(func(): Input.action_press("jump"))
	jmp_btn.button_up.connect(func(): Input.action_release("jump"))

	# 💨 Dodge button
	var ddg_btn = _create_action_btn(actions, "💨\nDODGE", Vector2(150, 40), Vector2(70, 70), Color(0.25, 0.75, 0.4, 0.85))
	ddg_btn.button_down.connect(func(): Input.action_press("dodge"))
	ddg_btn.button_up.connect(func(): Input.action_release("dodge"))

	# 🛐 Pray / Interact button
	var pry_btn = _create_action_btn(actions, "🛐\nPRAY", Vector2(65, 55), Vector2(65, 65), Color(0.9, 0.75, 0.2, 0.85))
	pry_btn.button_down.connect(func(): Input.action_press("interact_pray"))
	pry_btn.button_up.connect(func(): Input.action_release("interact_pray"))

	# 🛡 Shield Wall button
	var shd_btn = _create_action_btn(actions, "🛡\nPHALANX", Vector2(0, 0), Vector2(70, 50), Color(0.4, 0.5, 0.85, 0.85))
	shd_btn.button_down.connect(func(): Input.action_press("command_shield_wall"))
	shd_btn.button_up.connect(func(): Input.action_release("command_shield_wall"))

	# 🔄 Class Cycle button
	var cls_btn = _create_action_btn(actions, "🔄\nCLASS", Vector2(80, 0), Vector2(65, 50), Color(0.65, 0.35, 0.85, 0.85))
	cls_btn.button_down.connect(func(): Input.action_press("cycle_class"))
	cls_btn.button_up.connect(func(): Input.action_release("cycle_class"))

	# 📖 Lore / Codex button
	var cdx_btn = _create_action_btn(actions, "📖\nLORE", Vector2(155, -20), Vector2(65, 48), Color(0.8, 0.5, 0.2, 0.85))
	cdx_btn.button_down.connect(func(): Input.action_press("open_codex"))
	cdx_btn.button_up.connect(func(): Input.action_release("open_codex"))

func _create_touch_btn(parent: Control, label_text: String, pos: Vector2, sz: Vector2, action_name: String) -> Button:
	var btn = Button.new()
	btn.text = label_text
	btn.position = pos
	btn.size = sz
	btn.focus_mode = Control.FOCUS_NONE
	var style = StyleBoxFlat.new()
	style.bg_color = Color(0.1, 0.12, 0.2, 0.75)
	style.border_color = Color(0.85, 0.75, 0.3, 0.8)
	style.set_border_width_all(2)
	style.set_corner_radius_all(10)
	btn.add_theme_stylebox_override("normal", style)
	var pressed_style = style.duplicate()
	pressed_style.bg_color = Color(0.3, 0.35, 0.55, 0.9)
	btn.add_theme_stylebox_override("pressed", pressed_style)
	btn.add_theme_font_size_override("font_size", 22)
	btn.button_down.connect(func(): Input.action_press(action_name))
	btn.button_up.connect(func(): Input.action_release(action_name))
	parent.add_child(btn)
	return btn

func _create_action_btn(parent: Control, label_text: String, pos: Vector2, sz: Vector2, color: Color) -> Button:
	var btn = Button.new()
	btn.text = label_text
	btn.position = pos
	btn.size = sz
	btn.focus_mode = Control.FOCUS_NONE
	var style = StyleBoxFlat.new()
	style.bg_color = color
	style.border_color = Color(1.0, 0.9, 0.6, 0.9)
	style.set_border_width_all(2)
	style.set_corner_radius_all(sz.x / 2.0 if sz.x == sz.y else 10)
	btn.add_theme_stylebox_override("normal", style)
	var pressed_style = style.duplicate()
	pressed_style.bg_color = color.lightened(0.25)
	btn.add_theme_stylebox_override("pressed", pressed_style)
	btn.add_theme_font_size_override("font_size", 12 if "\n" in label_text else 14)
	parent.add_child(btn)
	return btn

