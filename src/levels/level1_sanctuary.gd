extends Node3D

@onready var camera_pivot = $CameraPivot
@onready var hud = $HUD
@onready var spawner = $DemonSpawner

func _ready():
	Scenery.populate(self)
	CampaignManager.current_level = 1
	CampaignManager.army_count = 0
	Input.set_mouse_mode(Input.MOUSE_MODE_CAPTURED)

	var player = get_tree().get_first_node_in_group("player")
	if player and hud:
		hud.setup_player_bindings(player)
		player.connect("died", Callable(self, "_on_player_died"))

	# Connect spawner signals to HUD
	if spawner and hud:
		spawner.connect("wave_started", Callable(hud, "update_wave_info"))
		spawner.connect("wave_progress", Callable(hud, "update_enemies_remaining"))
		spawner.connect("all_waves_cleared", Callable(self, "_on_sanctuary_cleared"))

	get_tree().create_timer(1.0).timeout.connect(func():
		SoundManager.play_dialogue("athena_intro", true)
		DivineManager.emit_signal("message_broadcast", "CHAPTER I: SANCTUARY OF OLYMPUS", "Athena: Look upon Mount Olympus and cleanse the sacred plaza!")
	)

func _process(delta):
	var player = get_tree().get_first_node_in_group("player")
	if is_instance_valid(player) and is_instance_valid(camera_pivot):
		camera_pivot.global_position = camera_pivot.global_position.lerp(player.global_position + Vector3(0, 1.4, 0), 12.0 * delta)

func _on_player_died():
	if hud:
		hud.show_game_over()

func _on_sanctuary_cleared():
	SoundManager.play_dialogue("warrior_victory")
	if hud:
		hud.show_victory("SANCTUARY DEFENDED!", "The vanguard is defeated! Advance to the Peloponnese Coast to intercept the Roman landing!")
