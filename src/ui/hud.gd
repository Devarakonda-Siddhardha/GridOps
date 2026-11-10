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

	# Initial slot setup
	for god in slots.keys():
		var slot = slots[god]
		var info = DivineManager.powers[god]
		slot.get_node("KeyLabel").text = "[" + info["key"] + "]"
		slot.get_node("NameLabel").text = info["name"]
		slot.get_node("StatusLabel").text = "LOCKED\n(Pray at Altar)"
		slot.get_node("CooldownOverlay").visible = false
		slot.modulate = Color(0.6, 0.6, 0.6, 0.6)

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
		wave_label.text = "WAVE %d / 3" % wave_num
	if enemy_count_label:
		enemy_count_label.text = "%d Demons Remaining" % total_enemies

func update_enemies_remaining(remaining: int, total_enemies: int):
	if enemy_count_label:
		enemy_count_label.text = "%d / %d Demons Remaining" % [remaining, total_enemies]

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

func show_victory():
	victory_panel.visible = true
	Input.set_mouse_mode(Input.MOUSE_MODE_VISIBLE)

func show_game_over():
	game_over_panel.visible = true
	Input.set_mouse_mode(Input.MOUSE_MODE_VISIBLE)

func _on_restart_pressed():
	get_tree().reload_current_scene()
