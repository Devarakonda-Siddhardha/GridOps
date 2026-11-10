extends Node3D

@onready var player = $Warrior
@onready var camera_pivot = $CameraPivot
@onready var hud = $HUD
@onready var boss = $GeneralMarcus
@onready var gate = $FortressGate

var gate_breached: bool = false
var boss_defeated: bool = false

func _ready():
	CampaignManager.current_level = 3

	if player and hud:
		player.connect("health_changed", Callable(hud, "update_hp"))
		player.connect("stamina_changed", Callable(hud, "update_stamina"))
		player.connect("died", Callable(self, "_on_player_died"))

	if boss and hud:
		boss.connect("boss_health_changed", Callable(hud, "update_boss_hp"))
		boss.connect("died", Callable(self, "_on_boss_died"))

	if gate:
		gate.connect("gate_destroyed", Callable(self, "_on_gate_breached"))

	hud.set_objective("Breach Fortress Gate & Slay General Marcus")

	# Spawn the Greek Army that the player liberated in Chapter 2
	_spawn_greek_phalanx()

	get_tree().create_timer(1.2).timeout.connect(func():
		SoundManager.play_dialogue("campaign_intro_3")
		DivineManager.emit_signal("message_broadcast", "CHAPTER III: SIEGE OF CASTRUM ROMA", "Lead your Greek Army to breach the gates, defeat General Marcus, and liberate Hellas!")
	)

func _spawn_greek_phalanx():
	var soldier_scene = load("res://src/allies/greek_soldier.tscn")
	var count = max(8, CampaignManager.army_count)
	CampaignManager.army_count = count

	for i in range(count):
		var s = soldier_scene.instantiate()
		s.squad_index = i
		add_child(s)
		var row = int(i / 4) + 1
		var col = (i % 4) - 1.5
		s.global_position = player.global_position + Vector3(col * 2.2, 0, row * 2.5)

func _process(delta):
	if is_instance_valid(player) and is_instance_valid(camera_pivot):
		camera_pivot.global_position = camera_pivot.global_position.lerp(player.global_position + Vector3(0, 1.4, 0), 12.0 * delta)

func _on_gate_breached():
	gate_breached = true
	hud.set_objective("Defeat General Marcus Aurelius!")

func _on_boss_died(general):
	boss_defeated = true
	get_tree().create_timer(2.0).timeout.connect(func():
		SoundManager.play_dialogue("campaign_victory")
		if hud:
			hud.show_victory("THE GREEK EMPIRE RECLAIMED!", "General Marcus Aurelius has fallen! The Roman legions have fled, and Hellas stands eternal!")
	)

func _on_player_died():
	if hud:
		hud.show_game_over()
