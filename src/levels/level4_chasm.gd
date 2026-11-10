extends Node3D

@onready var camera_pivot = $CameraPivot
@onready var hud = $HUD
@onready var minotaur = $BossContainer/Minotaur

var is_cleared: bool = false

func _ready():
	CampaignManager.current_level = 4
	Input.set_mouse_mode(Input.MOUSE_MODE_CAPTURED)

	_spawn_player()

	if minotaur and minotaur.has_signal("died"):
		minotaur.connect("died", Callable(self, "_on_minotaur_defeated"))

	if hud:
		hud.update_wave_info(4, 1)
		hud.set_objective("Vanquish the Infernal Minotaur & Seal the Abyss")

	get_tree().create_timer(1.2).timeout.connect(func():
		SoundManager.play_dialogue("biome_chasm")
		DivineManager.emit_signal("message_broadcast", "CHAPTER IV: THE CHASM OF TARTARUS", "Volcanic Ashlands! Slay the Infernal Minotaur to seal the Underworld rift!")
	)

func _spawn_player():
	var p_class = CampaignManager.selected_class
	var scene_path = CampaignManager.CLASS_SCENES.get(p_class, "res://src/player/warrior.tscn")
	var p_scene = load(scene_path)
	var p = p_scene.instantiate()
	add_child(p)
	p.global_position = Vector3(0, 0.5, 30)

	if camera_pivot:
		camera_pivot.target = p
		camera_pivot.global_position = p.global_position + Vector3(0, 1.4, 0)
	if hud:
		hud.setup_player_bindings(p)

func _process(delta):
	var player = get_tree().get_first_node_in_group("player")
	if is_instance_valid(player) and is_instance_valid(camera_pivot):
		camera_pivot.global_position = camera_pivot.global_position.lerp(player.global_position + Vector3(0, 1.4, 0), 12.0 * delta)

func _on_minotaur_defeated(_boss):
	if is_cleared:
		return
	is_cleared = true
	SoundManager.play_dialogue("campaign_victory")
	if hud:
		hud.show_victory("THE INFERNAL BEAST HAS FALLEN!", "The Tartarus chasm is sealed! Lead the Greek Phalanx into the final Siege of Castrum Roma!")
