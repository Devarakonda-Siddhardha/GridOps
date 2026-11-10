extends Node3D

@onready var camera_pivot = $CameraPivot
@onready var hud = $HUD
@onready var boss = $GeneralMarcus
@onready var gate = $FortressGate

var gate_breached: bool = false
var boss_defeated: bool = false

func _ready():
	CampaignManager.current_level = 5
	Input.set_mouse_mode(Input.MOUSE_MODE_CAPTURED)

	_spawn_player()

	if boss and hud:
		boss.connect("boss_health_changed", Callable(hud, "update_boss_hp"))
		boss.connect("died", Callable(self, "_on_boss_died"))

	if gate:
		gate.connect("gate_destroyed", Callable(self, "_on_gate_breached"))

	if hud:
		hud.update_wave_info(5, 1)
		hud.set_objective("Breach the Fortress Gate & Vanquish Legatus General Marcus")

	_spawn_greek_phalanx()

	get_tree().create_timer(1.2).timeout.connect(func():
		SoundManager.play_dialogue("athena_level5_siege", true)
		DivineManager.emit_signal("message_broadcast", "CHAPTER V: THE SIEGE OF CASTRUM ROMA", "Athena: Sound the charge! Breach the fortress gates and reclaim Hellas!")
	)

func _spawn_player():
	var p_class = CampaignManager.selected_class
	var scene_path = CampaignManager.CLASS_SCENES.get(p_class, "res://src/player/warrior.tscn")
	var p_scene = load(scene_path)
	var p = p_scene.instantiate()
	add_child(p)
	p.global_position = Vector3(0, 0.5, 48)

	if camera_pivot:
		camera_pivot.target = p
		camera_pivot.global_position = p.global_position + Vector3(0, 1.4, 0)
	if hud:
		hud.setup_player_bindings(p)

func _spawn_greek_phalanx():
	var soldier_scene = load("res://src/allies/greek_soldier.tscn")
	var count = max(12, CampaignManager.army_count)
	CampaignManager.army_count = count

	var player = get_tree().get_first_node_in_group("player")
	var p_pos = player.global_position if player else Vector3(0, 0, 48)

	for i in range(count):
		var s = soldier_scene.instantiate()
		s.squad_index = i
		add_child(s)
		var row = int(i / 4) + 1
		var col = (i % 4) - 1.5
		s.global_position = p_pos + Vector3(col * 2.2, 0, row * 2.5)

func _process(delta):
	var player = get_tree().get_first_node_in_group("player")
	if is_instance_valid(player) and is_instance_valid(camera_pivot):
		camera_pivot.global_position = camera_pivot.global_position.lerp(player.global_position + Vector3(0, 1.4, 0), 12.0 * delta)

func _on_gate_breached():
	gate_breached = true
	if hud:
		hud.set_objective("Storm the Courtyard: Defeat General Marcus Aurelius!")
	DivineManager.emit_signal("message_broadcast", "GATE BREACHED!", "Storm the courtyard with your Phalanx!")

func _on_boss_died(_general):
	boss_defeated = true
	get_tree().create_timer(2.0).timeout.connect(func():
		SoundManager.play_dialogue("athena_victory", true)
		if hud:
			hud.show_victory("THE GREEK EMPIRE IS RECLAIMED!", "Athena: Your courage and strategy have echoed into eternity. Hellas is free!")
	)
