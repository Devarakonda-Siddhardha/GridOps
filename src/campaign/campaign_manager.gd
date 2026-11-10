extends Node

signal army_changed(current_count: int, max_count: int)
signal army_command(command_type: String)
signal objective_updated(text: String)
signal level_completed(level_num: int)

var current_level: int = 1
var army_count: int = 0
var max_army_count: int = 16

var rescued_cages: int = 0
var total_cages: int = 3

var level_scenes = {
	1: "res://src/levels/level1_sanctuary.tscn",
	2: "res://src/levels/level2_valley.tscn",
	3: "res://src/levels/level3_siege.tscn"
}

func _ready():
	process_mode = Node.PROCESS_MODE_ALWAYS

func _input(event):
	if event is InputEventKey and event.is_pressed() and not event.is_echo():
		if event.keycode == KEY_G:
			order_charge()
		elif event.keycode == KEY_H:
			order_regroup()

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

func order_regroup():
	emit_signal("army_command", "regroup")
	DivineManager.emit_signal("message_broadcast", "REGROUP PHALANX!", "Soldiers falling back to defensive formation!")

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
