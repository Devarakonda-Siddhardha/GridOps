extends Node

signal wave_started(wave_num, total_enemies)
signal wave_progress(enemies_remaining, total_enemies)
signal all_waves_cleared

@export var demon_scene: PackedScene = preload("res://src/enemies/demon.tscn")
@export var spawn_radius: float = 22.0

var current_wave: int = 0
var total_waves: int = 3
var active_demons: int = 0
var total_in_wave: int = 0
var wave_in_progress: bool = false

var wave_configs = [
	{"count": 3, "boss": false, "title": "Wave 1: Scouts of Tartarus"},
	{"count": 5, "boss": false, "title": "Wave 2: Underworld Siege"},
	{"count": 7, "boss": true,  "title": "Wave 3: The Pit Warlord Awakens"}
]

func _ready():
	# Start Wave 1 after short intro delay
	get_tree().create_timer(2.0).timeout.connect(start_next_wave)

func start_next_wave():
	if current_wave >= total_waves:
		emit_signal("all_waves_cleared")
		return

	current_wave += 1
	var cfg = wave_configs[current_wave - 1]
	total_in_wave = cfg["count"] + (1 if cfg["boss"] else 0)
	active_demons = total_in_wave
	wave_in_progress = true

	emit_signal("wave_started", current_wave, total_in_wave)
	DivineManager.emit_signal("message_broadcast", cfg["title"].to_upper(), "Pray to the Gods and purge the demons!")

	if current_wave == 1:
		get_tree().create_timer(1.2).timeout.connect(func():
			SoundManager.play_dialogue("demon_spawn")
		)

	# Stagger spawns around the arena perimeter
	var arena = get_tree().current_scene
	var player = get_tree().get_first_node_in_group("player")
	var player_pos = player.global_position if player else Vector3.ZERO

	for i in range(cfg["count"]):
		get_tree().create_timer(i * 0.4).timeout.connect(func():
			_spawn_demon(false, player_pos)
		)

	if cfg["boss"]:
		get_tree().create_timer(cfg["count"] * 0.4 + 1.0).timeout.connect(func():
			_spawn_demon(true, player_pos)
		)

func _spawn_demon(is_boss: bool, center: Vector3):
	var demon = demon_scene.instantiate()
	demon.is_boss = is_boss

	if is_boss:
		demon.max_health = 360.0
		demon.attack_damage = 32.0
		demon.scale = Vector3(1.4, 1.4, 1.4)

	# Add to tree first so global transform is valid
	var root = get_tree().current_scene
	root.add_child(demon)

	# Random angle along spawn radius
	var angle = randf() * TAU
	var spawn_pos = center + Vector3(sin(angle) * spawn_radius, 0.5, cos(angle) * spawn_radius)
	demon.global_position = spawn_pos

	demon.connect("died", Callable(self, "_on_demon_died"))

func _on_demon_died(demon):
	active_demons = max(0, active_demons - 1)
	emit_signal("wave_progress", active_demons, total_in_wave)

	if active_demons <= 0 and wave_in_progress:
		wave_in_progress = false
		if current_wave < total_waves:
			DivineManager.emit_signal("message_broadcast", "WAVE %d PURGED!" % current_wave, "Prepare yourself for the next assault...")
			get_tree().create_timer(3.5).timeout.connect(start_next_wave)
		else:
			emit_signal("all_waves_cleared")
			DivineManager.emit_signal("message_broadcast", "OLYMPUS PREVAILS!", "You have cleansed the sacred sanctuary of Tartarus.")
