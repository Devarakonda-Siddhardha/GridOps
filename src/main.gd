extends Node3D

@onready var player = $Warrior
@onready var camera_pivot = $CameraPivot
@onready var hud = $HUD
@onready var spawner = $DemonSpawner

func _ready():
	# Connect player signals to HUD
	if player and hud:
		player.connect("health_changed", Callable(hud, "update_hp"))
		player.connect("stamina_changed", Callable(hud, "update_stamina"))
		player.connect("died", Callable(self, "_on_player_died"))

	# Connect spawner signals to HUD
	if spawner and hud:
		spawner.connect("wave_started", Callable(hud, "update_wave_info"))
		spawner.connect("wave_progress", Callable(hud, "update_enemies_remaining"))
		spawner.connect("all_waves_cleared", Callable(self, "_on_all_waves_cleared"))

	get_tree().create_timer(1.0).timeout.connect(func():
		SoundManager.play_dialogue("warrior_intro")
	)

func _process(delta):
	# Follow player with camera pivot
	if is_instance_valid(player) and is_instance_valid(camera_pivot):
		camera_pivot.global_position = camera_pivot.global_position.lerp(player.global_position + Vector3(0, 1.4, 0), 12.0 * delta)

func _on_player_died():
	if hud:
		hud.show_game_over()

func _on_all_waves_cleared():
	SoundManager.play_dialogue("warrior_victory")
	if hud:
		hud.show_victory()
