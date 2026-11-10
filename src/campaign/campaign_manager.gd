extends Node

signal army_changed(current_count: int, max_count: int)
signal army_command(command_type: String)
signal objective_updated(text: String)
signal level_completed(level_num: int)
signal hero_class_changed(hero_type: String)
signal codex_toggled

var current_level: int = 1
var army_count: int = 0
var max_army_count: int = 24

var rescued_cages: int = 0
var total_cages: int = 3

var selected_class: String = "warrior" # "warrior", "archer", "cavalry"

const CLASS_SCENES = {
	"warrior": "res://src/player/warrior.tscn",
	"archer": "res://src/player/archer.tscn",
	"cavalry": "res://src/player/cavalry.tscn"
}

var level_scenes = {
	1: "res://src/levels/level1_sanctuary.tscn",
	2: "res://src/levels/level2_coast.tscn",
	3: "res://src/levels/level3_valley.tscn",
	4: "res://src/levels/level4_chasm.tscn",
	5: "res://src/levels/level5_siege.tscn",
	6: "res://src/levels/level6_thermopylae.tscn",
	7: "res://src/levels/level7_delphi.tscn",
	8: "res://src/levels/level8_delos.tscn",
	9: "res://src/levels/level9_appian_way.tscn",
	10: "res://src/levels/level10_rome_colosseum.tscn"
}

func _ready():
	process_mode = Node.PROCESS_MODE_ALWAYS

func _input(event):
	if event is InputEventKey and event.is_pressed() and not event.is_echo():
		if event.keycode == KEY_G:
			order_charge()
		elif event.keycode == KEY_H:
			order_shield_wall()
		elif event.keycode == KEY_V:
			order_regroup()
		elif event.keycode == KEY_B or event.keycode == KEY_P:
			toggle_codex()
		elif event.keycode == KEY_T or event.keycode == KEY_TAB:
			cycle_hero_class()

func recruit_allies(amount: int):
	army_count = min(max_army_count, army_count + amount)
	emit_signal("army_changed", army_count, max_army_count)
	SoundManager.play_dialogue("ally_rescued")

func ally_died():
	army_count = max(0, army_count - 1)
	emit_signal("army_changed", army_count, max_army_count)

func order_charge():
	emit_signal("army_command", "charge")
	SoundManager.play_dialogue("ally_charge")
	DivineManager.emit_signal("message_broadcast", "ARMY CHARGE!", "Greek Phalanx charging enemy lines!")

func order_shield_wall():
	emit_signal("army_command", "shield_wall")
	SoundManager.play("shield_block", 1.0)
	DivineManager.emit_signal("message_broadcast", "SHIELD WALL!", "Hoplites raise shields in phalanx formation! (65% damage reduction)")

func order_regroup():
	emit_signal("army_command", "regroup")
	DivineManager.emit_signal("message_broadcast", "REGROUP PHALANX!", "Soldiers falling back to defensive formation!")

func toggle_codex():
	emit_signal("codex_toggled")

func cycle_hero_class():
	var classes = ["warrior", "archer", "cavalry"]
	var idx = classes.find(selected_class)
	var nxt = classes[(idx + 1) % classes.size()]
	switch_hero_class(nxt)

func switch_hero_class(new_class: String):
	if not CLASS_SCENES.has(new_class):
		return

	var current_player = get_tree().get_first_node_in_group("player")
	if not current_player:
		selected_class = new_class
		emit_signal("hero_class_changed", new_class)
		return

	var scene_root = current_player.get_parent()
	var spawn_pos = current_player.global_position
	var spawn_rot = current_player.rotation

	# Free old player
	current_player.remove_from_group("player")
	current_player.queue_free()

	# Instantiate new player class
	selected_class = new_class
	var new_scene = load(CLASS_SCENES[new_class])
	var new_player = new_scene.instantiate()
	new_player.global_position = spawn_pos
	new_player.rotation = spawn_rot
	scene_root.add_child(new_player)

	# Update camera pivot target
	var cam_pivot = scene_root.get_node_or_null("CameraPivot")
	if cam_pivot:
		cam_pivot.target = new_player

	# Update HUD connections
	var hud = scene_root.get_node_or_null("HUD")
	if hud and hud.has_method("setup_player_bindings"):
		hud.setup_player_bindings(new_player)

	emit_signal("hero_class_changed", new_class)
	var display_name = "SPARTAN CHAMPION" if new_class == "warrior" else ("CRETAN ARCHER" if new_class == "archer" else "THESSALIAN CAVALRY")
	DivineManager.emit_signal("message_broadcast", "CLASS SWITCHED", "Now playing as %s!" % display_name)

func load_level(level_num: int):
	current_level = level_num
	if level_scenes.has(level_num):
		get_tree().change_scene_to_file(level_scenes[level_num])

func advance_to_next_level():
	var nxt = current_level + 1
	if level_scenes.has(nxt):
		load_level(nxt)
	else:
		load_level(1)
