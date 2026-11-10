extends Node3D

@onready var camera_pivot = $CameraPivot
@onready var hud = $HUD
@onready var enemies_container = $Enemies

var total_enemies: int = 0
var remaining_enemies: int = 0
var is_cleared: bool = false

func _ready():
	CampaignManager.current_level = 8
	Input.set_mouse_mode(Input.MOUSE_MODE_CAPTURED)

	_spawn_player()
	_spawn_greek_phalanx()

	total_enemies = enemies_container.get_child_count()
	remaining_enemies = total_enemies

	for enemy in enemies_container.get_children():
		if enemy.has_signal("died"):
			enemy.connect("died", Callable(self, "_on_enemy_killed"))

	if hud:
		hud.update_wave_info(8, total_enemies)
		hud.set_objective("Seize the Roman Fleet & Liberate Delos (%d Remaining)" % remaining_enemies)

	get_tree().create_timer(1.2).timeout.connect(func():
		SoundManager.play_dialogue("athena_level8_delos", true)
		DivineManager.emit_signal("message_broadcast", "CHAPTER VIII: ISLE OF DELOS", "Athena: Seize their fleet of warships and liberate our trapped brothers! Today, Greece takes the war to Roman shores!")
	)

func _spawn_player():
	var p_class = CampaignManager.selected_class
	var scene_path = CampaignManager.CLASS_SCENES.get(p_class, "res://src/player/warrior.tscn")
	var p_scene = load(scene_path)
	var p = p_scene.instantiate()
	add_child(p)
	p.global_position = Vector3(0, 0.5, 42)

	if camera_pivot:
		camera_pivot.target = p
		camera_pivot.global_position = p.global_position + Vector3(0, 1.4, 0)
	if hud:
		hud.setup_player_bindings(p)

func _spawn_greek_phalanx():
	var soldier_scene = load("res://src/allies/greek_soldier.tscn")
	var count = max(10, CampaignManager.army_count)
	CampaignManager.army_count = count

	var player = get_tree().get_first_node_in_group("player")
	var p_pos = player.global_position if player else Vector3(0, 0, 42)

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

func _on_enemy_killed(_enemy):
	remaining_enemies = max(0, remaining_enemies - 1)
	if hud:
		hud.update_enemies_remaining(remaining_enemies, total_enemies)

	if remaining_enemies == 0 and not is_cleared:
		is_cleared = true
		_on_delos_cleared()

func _on_delos_cleared():
	SoundManager.play_dialogue("campaign_victory")
	if hud:
		hud.show_victory("THE FLEET IS SEIZED!", "The Roman triremes belong to Greece! Set sail across the Adriatic Sea to the Appian Way!")
