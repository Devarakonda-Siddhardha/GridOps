extends Node3D

@onready var camera_pivot = $CameraPivot
@onready var hud = $HUD
@onready var enemies_container = $Enemies

var total_enemies: int = 0
var remaining_enemies: int = 0
var is_cleared: bool = false

func _ready():
	CampaignManager.current_level = 2
	Input.set_mouse_mode(Input.MOUSE_MODE_CAPTURED)

	# Instantiate selected hero class
	_spawn_player()

	# Count enemies
	total_enemies = enemies_container.get_child_count()
	remaining_enemies = total_enemies

	for enemy in enemies_container.get_children():
		if enemy.has_signal("died"):
			enemy.connect("died", Callable(self, "_on_enemy_killed"))

	if hud:
		hud.update_wave_info(2, total_enemies)
		hud.set_objective("Defeat the Roman Beachhead Garrison (%d Remaining)" % remaining_enemies)

	get_tree().create_timer(1.2).timeout.connect(func():
		SoundManager.play_dialogue("biome_coast")
		DivineManager.emit_signal("message_broadcast", "CHAPTER II: THE COAST OF PELOPONNESE", "The Roman fleet has landed! Vanquish the vanguard and burn their landing force!")
	)

func _spawn_player():
	var p_class = CampaignManager.selected_class
	var scene_path = CampaignManager.CLASS_SCENES.get(p_class, "res://src/player/warrior.tscn")
	var p_scene = load(scene_path)
	var p = p_scene.instantiate()
	add_child(p)
	p.global_position = Vector3(0, 0.5, 40)

	if camera_pivot:
		camera_pivot.target = p
		camera_pivot.global_position = p.global_position + Vector3(0, 1.4, 0)
	if hud:
		hud.setup_player_bindings(p)

func _process(delta):
	var player = get_tree().get_first_node_in_group("player")
	if is_instance_valid(player) and is_instance_valid(camera_pivot):
		camera_pivot.global_position = camera_pivot.global_position.lerp(player.global_position + Vector3(0, 1.4, 0), 12.0 * delta)

func _on_enemy_killed(_enemy):
	remaining_enemies = max(0, remaining_enemies - 1)
	if hud:
		hud.update_enemies_remaining(remaining_enemies, total_enemies)

	if remaining_enemies == 0 and not is_cleared:
		is_cleared = true
		_on_coast_cleared()

func _on_coast_cleared():
	SoundManager.play_dialogue("campaign_victory")
	if hud:
		hud.show_victory("BEACHHEAD SECURED!", "The Roman landing force is crushed! Advance into Arcadia Valley!")
