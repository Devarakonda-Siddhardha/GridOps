extends Node

var sounds = {}
var pool_size = 12
var players = []
var next_player_idx = 0

func _ready():
	_load_sound("sword_swing", "res://assets/audio/sword_swing.wav")
	_load_sound("sword_hit", "res://assets/audio/sword_hit.wav")
	_load_sound("lightning", "res://assets/audio/lightning.wav")
	_load_sound("water_wave", "res://assets/audio/water_wave.wav")
	_load_sound("soul_drain", "res://assets/audio/soul_drain.wav")
	_load_sound("ares_fury", "res://assets/audio/ares_fury.wav")
	_load_sound("prayer", "res://assets/audio/prayer_chant.wav")
	_load_sound("demon_roar", "res://assets/audio/demon_roar.wav")
	_load_sound("demon_death", "res://assets/audio/demon_death.wav")
	_load_sound("player_hurt", "res://assets/audio/player_hurt.wav")

	# Create player pool
	for i in range(pool_size):
		var p = AudioStreamPlayer.new()
		add_child(p)
		players.append(p)

func _load_sound(sound_name: String, path: String):
	if FileAccess.file_exists(path):
		var s = load(path)
		sounds[sound_name] = s

func play(sound_name: String, pitch: float = 1.0, volume_db: float = 0.0):
	if not sounds.has(sound_name):
		return
	var stream = sounds[sound_name]
	var p = players[next_player_idx]
	next_player_idx = (next_player_idx + 1) % pool_size
	p.stream = stream
	p.pitch_scale = pitch * randf_range(0.95, 1.05)
	p.volume_db = volume_db
	p.play()
