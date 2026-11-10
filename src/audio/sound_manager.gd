extends Node

signal dialogue_started(speaker: String, text: String, color: Color, duration: float)

var sounds = {}
var pool_size = 16
var players = []
var next_player_idx = 0
var dialogue_player: AudioStreamPlayer

var last_dialogue_time: float = -10.0
var min_dialogue_interval: float = 1.2

var dialogues = {
	"warrior_intro": {
		"speaker": "Spartan Warrior",
		"text": "By the gods of Olympus, no Roman oppressor shall leave this arena alive!",
		"color": Color(1.0, 0.85, 0.3)
	},
	"warrior_pray": {
		"speaker": "Spartan Warrior",
		"text": "Hear me, Immortals! Grant me divine power!",
		"color": Color(1.0, 0.85, 0.3)
	},
	"warrior_attack": {
		"speaker": "Spartan Warrior",
		"text": "For Sparta! Die!",
		"color": Color(1.0, 0.85, 0.3)
	},
	"warrior_hurt": {
		"speaker": "Spartan Warrior",
		"text": "You will pay for that!",
		"color": Color(1.0, 0.5, 0.3)
	},
	"warrior_victory": {
		"speaker": "Spartan Warrior",
		"text": "Olympus stands undefeated!",
		"color": Color(1.0, 0.9, 0.4)
	},
	"god_zeus_blessing": {
		"speaker": "Zeus, Lord of Olympus",
		"text": "I am Zeus, King of Olympus! Smite the Roman defilers with my thunderbolts!",
		"color": Color(0.4, 0.85, 1.0)
	},
	"god_zeus_cast": {
		"speaker": "Zeus",
		"text": "Feel the wrath of Olympus!",
		"color": Color(0.4, 0.85, 1.0)
	},
	"god_poseidon_blessing": {
		"speaker": "Poseidon, Lord of the Oceans",
		"text": "I am Poseidon, Lord of the Oceans! Let the crushing tides swallow your foes!",
		"color": Color(0.2, 0.95, 0.85)
	},
	"god_poseidon_cast": {
		"speaker": "Poseidon",
		"text": "The ocean depths answer my call!",
		"color": Color(0.2, 0.95, 0.85)
	},
	"god_hades_blessing": {
		"speaker": "Hades, Ruler of the Dead",
		"text": "I am Hades, Ruler of the Dead. Claim their souls and drag them to the abyss!",
		"color": Color(0.75, 0.35, 1.0)
	},
	"god_hades_cast": {
		"speaker": "Hades",
		"text": "Your soul belongs to Tartarus!",
		"color": Color(0.75, 0.35, 1.0)
	},
	"god_ares_blessing": {
		"speaker": "Ares, God of War",
		"text": "I am Ares, God of War! Let blood spill and carnage reign upon this sacred arena!",
		"color": Color(1.0, 0.25, 0.15)
	},
	"god_ares_cast": {
		"speaker": "Ares",
		"text": "Spartan Berserk! Unleash the fury!",
		"color": Color(1.0, 0.25, 0.15)
	},
	"demon_spawn": {
		"speaker": "Roman Vanguard",
		"text": "Mortal flesh shall burn in the pits!",
		"color": Color(0.9, 0.2, 0.2)
	},
	"demon_defeat": {
		"speaker": "Tartarus Fiend",
		"text": "The darkness... will return!",
		"color": Color(0.6, 0.15, 0.15)
	},
	"general_intro": {
		"speaker": "General Marcus",
		"text": "You dare challenge the eternal might of Rome, barbarian dog? You will kneel!",
		"color": Color(0.85, 0.25, 0.95)
	},
	"general_testudo": {
		"speaker": "General Marcus",
		"text": "Legions, form the testudo! Crush their pathetic rebellion!",
		"color": Color(0.85, 0.25, 0.95)
	},
	"general_defeat": {
		"speaker": "General Marcus",
		"text": "Impossible... Rome cannot fall to a Greek mongrel...",
		"color": Color(0.85, 0.25, 0.95)
	},
	"centurion_shout": {
		"speaker": "Roman Centurion",
		"text": "Cohort, advance! Draw your gladii and leave none alive!",
		"color": Color(0.95, 0.2, 0.2)
	},
	"ally_rescued": {
		"speaker": "Freed Greek Hoplite",
		"text": "We are free! Lead us to war, Spartan Champion!",
		"color": Color(0.3, 0.7, 1.0)
	},
	"ally_charge": {
		"speaker": "Greek Phalanx",
		"text": "For the glory of Hellas! Advance the Phalanx!",
		"color": Color(0.3, 0.7, 1.0)
	},
	"campaign_intro_2": {
		"speaker": "Oracle of Delphi",
		"text": "Arcadia is overrun by Roman outposts. Liberate our captured brothers and rally the Phalanx!",
		"color": Color(1.0, 0.85, 0.3)
	},
	"campaign_intro_3": {
		"speaker": "Oracle of Delphi",
		"text": "Behold Castrum Roma! Breach the fortress gate, vanquish the Legion, and reclaim Hellas!",
		"color": Color(1.0, 0.85, 0.3)
	},
	"campaign_victory": {
		"speaker": "Oracle of Delphi",
		"text": "The Roman Eagle has fallen! The glory of the Greek Empire rises once more!",
		"color": Color(1.0, 0.9, 0.4)
	}
}

func _ready():
	# Sound effects
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

	# Campaign SFX
	_load_sound("war_horn_roman", "res://assets/audio/war_horn_roman.wav")
	_load_sound("gate_smash", "res://assets/audio/gate_smash.wav")
	_load_sound("cage_break", "res://assets/audio/cage_break.wav")
	_load_sound("shield_block", "res://assets/audio/shield_block.wav")

	# Dialogues
	_load_sound("warrior_intro", "res://assets/audio/warrior_intro.wav")
	_load_sound("warrior_pray", "res://assets/audio/warrior_pray.wav")
	_load_sound("warrior_attack", "res://assets/audio/warrior_attack.wav")
	_load_sound("warrior_hurt", "res://assets/audio/warrior_hurt.wav")
	_load_sound("warrior_victory", "res://assets/audio/warrior_victory.wav")

	_load_sound("god_zeus_blessing", "res://assets/audio/god_zeus_blessing.wav")
	_load_sound("god_zeus_cast", "res://assets/audio/god_zeus_cast.wav")
	_load_sound("god_poseidon_blessing", "res://assets/audio/god_poseidon_blessing.wav")
	_load_sound("god_poseidon_cast", "res://assets/audio/god_poseidon_cast.wav")
	_load_sound("god_hades_blessing", "res://assets/audio/god_hades_blessing.wav")
	_load_sound("god_hades_cast", "res://assets/audio/god_hades_cast.wav")
	_load_sound("god_ares_blessing", "res://assets/audio/god_ares_blessing.wav")
	_load_sound("god_ares_cast", "res://assets/audio/god_ares_cast.wav")

	_load_sound("demon_spawn", "res://assets/audio/demon_spawn.wav")
	_load_sound("demon_defeat", "res://assets/audio/demon_defeat.wav")

	_load_sound("general_intro", "res://assets/audio/general_intro.wav")
	_load_sound("general_testudo", "res://assets/audio/general_testudo.wav")
	_load_sound("general_defeat", "res://assets/audio/general_defeat.wav")
	_load_sound("centurion_shout", "res://assets/audio/centurion_shout.wav")
	_load_sound("ally_rescued", "res://assets/audio/ally_rescued.wav")
	_load_sound("ally_charge", "res://assets/audio/ally_charge.wav")
	_load_sound("campaign_intro_2", "res://assets/audio/campaign_intro_2.wav")
	_load_sound("campaign_intro_3", "res://assets/audio/campaign_intro_3.wav")
	_load_sound("campaign_victory", "res://assets/audio/campaign_victory.wav")

	# Create SFX player pool
	for i in range(pool_size):
		var p = AudioStreamPlayer.new()
		add_child(p)
		players.append(p)

	# Dedicated Dialogue player
	dialogue_player = AudioStreamPlayer.new()
	dialogue_player.volume_db = 4.0
	add_child(dialogue_player)

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
	p.pitch_scale = pitch * randf_range(0.97, 1.03)
	p.volume_db = volume_db
	p.play()

func play_dialogue(key: String, force: bool = false):
	var current_time = Time.get_ticks_msec() / 1000.0
	if not force and (current_time - last_dialogue_time) < min_dialogue_interval:
		return
	if not sounds.has(key):
		return

	var stream = sounds[key]
	dialogue_player.stream = stream
	dialogue_player.pitch_scale = 1.0
	dialogue_player.play()
	last_dialogue_time = current_time

	if dialogues.has(key):
		var info = dialogues[key]
		var dur = 3.5
		if stream is AudioStream:
			dur = max(2.5, stream.get_length())
		emit_signal("dialogue_started", info["speaker"], info["text"], info["color"], dur)
