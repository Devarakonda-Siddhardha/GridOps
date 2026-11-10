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
	SoundManager.connect("dialogue_started", Callable(self, "_on_dialogue_started"))

	CampaignManager.connect("army_changed", Callable(self, "_on_army_changed"))
	CampaignManager.connect("objective_updated", Callable(self, "set_objective"))

	_create_dialogue_ui()
	_create_army_ui()
	_create_boss_bar_ui()
	_setup_victory_panel()

	# Initial slot setup
	for god in slots.keys():
		var slot = slots[god]
		var info = DivineManager.powers[god]
		slot.get_node("KeyLabel").text = "[" + info["key"] + "]"
		slot.get_node("NameLabel").text = info["name"]
		slot.get_node("StatusLabel").text = "LOCKED\n(Pray at Altar)" if not info["unlocked"] else info["title"]
		slot.get_node("CooldownOverlay").visible = false
		slot.modulate = Color(1.0, 1.0, 1.0, 1.0) if info["unlocked"] else Color(0.6, 0.6, 0.6, 0.6)

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
	army_hint_label.text = "[G] Order Charge   [H] Regroup"
	army_hint_label.add_theme_font_size_override("font_size", 11)
	army_hint_label.add_theme_color_override("font_color", Color(0.85, 0.85, 0.85))
	vbox.add_child(army_hint_label)

	_on_army_changed(CampaignManager.army_count, CampaignManager.max_army_count)

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
