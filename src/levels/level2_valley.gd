extends Node3D

@onready var player = $Warrior
@onready var camera_pivot = $CameraPivot
@onready var hud = $HUD

var total_camps: int = 3
var camps_liberated: int = 0
var level_cleared: bool = false

func _ready():
	CampaignManager.current_level = 2
	CampaignManager.rescued_cages = 0
	CampaignManager.total_cages = 3

	if player and hud:
		player.connect("health_changed", Callable(hud, "update_hp"))
		player.connect("stamina_changed", Callable(hud, "update_stamina"))
		player.connect("died", Callable(self, "_on_player_died"))

	hud.set_objective("Liberate 3 Prisoner Outposts (0 / 3)")

	get_tree().create_timer(1.2).timeout.connect(func():
		SoundManager.play_dialogue("campaign_intro_2")
		DivineManager.emit_signal("message_broadcast", "CHAPTER II: THE VALLEY OF ARCADIA", "Storm the Roman garrisons, liberate captured Spartans, and build your Army!")
	)

func _process(delta):
	if is_instance_valid(player) and is_instance_valid(camera_pivot):
		camera_pivot.global_position = camera_pivot.global_position.lerp(player.global_position + Vector3(0, 1.4, 0), 12.0 * delta)

	if not level_cleared and CampaignManager.rescued_cages >= total_camps:
		_check_valley_clear()

func _check_valley_clear():
	# Check if all enemies in the outposts are cleared
	var enemies = get_tree().get_nodes_in_group("enemies")
	var living_enemies = 0
	for e in enemies:
		if is_instance_valid(e) and not (e.get("is_dead") == true):
			living_enemies += 1

	if living_enemies == 0 and not level_cleared:
		level_cleared = true
		_on_valley_cleared()
	else:
		if hud:
			hud.set_objective("Camp Cages Freed! Defeat remaining Romans: %d" % living_enemies)

func _on_valley_cleared():
	SoundManager.play_dialogue("ally_charge")
	if hud:
		hud.show_victory("ARCADIA LIBERATED!", "With 12 Greek Hoplites at your side, march upon Castrum Roma to reclaim Hellas!")

func _on_player_died():
	if hud:
		hud.show_game_over()
