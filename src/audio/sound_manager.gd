extends Node

signal dialogue_started(speaker: String, text: String, color: Color, duration: float)

var sounds = {}
var pool_size = 16
var players = []
var next_player_idx = 0
var dialogue_player: AudioStreamPlayer
var athena_player: AudioStreamPlayer
var music_player: AudioStreamPlayer

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
	},
	"zeus_manifest": {
		"speaker": "Zeus, King of the Gods",
		"text": "I am Zeus, King of the Gods! The heavens shake at your devotion. Smite the Roman invaders with celestial lightning!",
		"color": Color(0.4, 0.85, 1.0)
	},
	"poseidon_manifest": {
		"speaker": "Poseidon, Master of Oceans",
		"text": "Mortal! I am Poseidon, master of the ocean depths! Unleash my crushing tidal waves and drown their legions!",
		"color": Color(0.2, 0.95, 0.85)
	},
	"hades_manifest": {
		"speaker": "Hades, Sovereign of Underworld",
		"text": "I am Hades, sovereign of the Underworld. No Roman soul shall escape the abyssal grasp of Tartarus!",
		"color": Color(0.75, 0.35, 1.0)
	},
	"ares_manifest": {
		"speaker": "Ares, God of War",
		"text": "Ares is with you! Spill their blood, crack their shields, and make the earth drown in Roman carnage!",
		"color": Color(1.0, 0.25, 0.15)
	},
	"archer_select": {
		"speaker": "Cretan Toxotes",
		"text": "My bow is strung. Not a single Roman shall escape my arrows!",
		"color": Color(0.3, 0.9, 0.5)
	},
	"archer_shoot": {
		"speaker": "Cretan Toxotes",
		"text": "Arrows away! For Hellas!",
		"color": Color(0.3, 0.9, 0.5)
	},
	"cavalry_select": {
		"speaker": "Thessalian Hippeus",
		"text": "The Thessalian cavalry rides! Trample them beneath iron hooves!",
		"color": Color(0.9, 0.65, 0.2)
	},
	"cavalry_charge": {
		"speaker": "Thessalian Hippeus",
		"text": "Charge! Ride them down!",
		"color": Color(0.9, 0.65, 0.2)
	},
	"roman_archer_shout": {
		"speaker": "Roman Sagittarii",
		"text": "Sagittarii, rain arrows upon them!",
		"color": Color(0.95, 0.3, 0.3)
	},
	"roman_cavalry_charge": {
		"speaker": "Roman Equites",
		"text": "Equites, charge! Break their formation!",
		"color": Color(0.95, 0.3, 0.3)
	},
	"minotaur_bellow": {
		"speaker": "Infernal Minotaur",
		"text": "Raaaargh! Slay the Greek mortal!",
		"color": Color(1.0, 0.15, 0.15)
	},
	"biome_coast": {
		"speaker": "Oracle of Delphi",
		"text": "The Roman fleet has landed on the shores of Peloponnese! Burn their triremes and push them into the sea!",
		"color": Color(1.0, 0.85, 0.3)
	},
	"biome_chasm": {
		"speaker": "Oracle of Delphi",
		"text": "A dark fissure to Tartarus has opened! Vanquish the Infernal Minotaur before the abyss swallows Greece!",
		"color": Color(1.0, 0.85, 0.3)
	},
	"athena_intro": {
		"speaker": "Athena, Goddess of Wisdom",
		"text": "Champion of Hellas, hear my voice. I am Athena. Look upon Mount Olympus. The Underworld claws at our holy mount. Take up your blade and cleanse the sacred plaza!",
		"color": Color(1.0, 0.85, 0.25)
	},
	"athena_pray_zeus": {
		"speaker": "Athena",
		"text": "Zeus, Lord of Olympus, watches from above. Kneel before the King of the Gods and let lightning empower your strikes.",
		"color": Color(1.0, 0.85, 0.25)
	},
	"athena_pray_poseidon": {
		"speaker": "Athena",
		"text": "Poseidon's tides crash against the shores of Hellas. Channel his oceanic fury to shatter enemy ranks.",
		"color": Color(1.0, 0.85, 0.25)
	},
	"athena_pray_hades": {
		"speaker": "Athena",
		"text": "Hades holds the subterranean gates of Tartarus. Even in death, there is power. Claim his dark siphon.",
		"color": Color(1.0, 0.85, 0.25)
	},
	"athena_pray_ares": {
		"speaker": "Athena",
		"text": "Ares thirsts for battle. Let rage fuel your blade, but remember: true victory is won through wisdom.",
		"color": Color(1.0, 0.85, 0.25)
	},
	"athena_class_archer": {
		"speaker": "Athena",
		"text": "A Cretan Toxotes bow! Strike with precision from afar. Distance and positioning are your greatest allies.",
		"color": Color(1.0, 0.85, 0.25)
	},
	"athena_class_cavalry": {
		"speaker": "Athena",
		"text": "A Thessalian warhorse! Trample the enemy cohorts beneath heavy hooves and spearhead our assault!",
		"color": Color(1.0, 0.85, 0.25)
	},
	"athena_class_champion": {
		"speaker": "Athena",
		"text": "The shield of Sparta! Unyielding and steadfast, hold the line against all odds.",
		"color": Color(1.0, 0.85, 0.25)
	},
	"athena_level2_coast": {
		"speaker": "Athena",
		"text": "We have reached the Peloponnese shoreline. The Roman fleet has beached their triremes. Burn their vanguard before they establish a foothold!",
		"color": Color(1.0, 0.85, 0.25)
	},
	"athena_level3_valley": {
		"speaker": "Athena",
		"text": "The Great Valley of Arcadia lies in chains. Roman outposts patrol these hills. Find the captured Spartan cages, liberate our soldiers, and assemble the Phalanx!",
		"color": Color(1.0, 0.85, 0.25)
	},
	"athena_army_assembled": {
		"speaker": "Athena",
		"text": "Our brothers in arms are free! Command them with courage. Together, no Roman legion can withstand the Greek Phalanx.",
		"color": Color(1.0, 0.85, 0.25)
	},
	"athena_level4_chasm": {
		"speaker": "Athena",
		"text": "The earth tears open into Tartarus. Beware the Infernal Minotaur! Dodge his ground-slam shockwaves and strike true!",
		"color": Color(1.0, 0.85, 0.25)
	},
	"athena_level5_siege": {
		"speaker": "Athena",
		"text": "Behold, Castrum Roma! Marcus Aurelius hides behind stone ramparts. Sound the charge! Breach the fortress gates and reclaim the glory of Hellas!",
		"color": Color(1.0, 0.85, 0.25)
	},
	"athena_level6_thermopylae": {
		"speaker": "Athena",
		"text": "We stand at the Hot Gates of Thermopylae! Form the shield wall across the narrow pass. Let their cohorts break against our bronze!",
		"color": Color(1.0, 0.85, 0.25)
	},
	"athena_level7_delphi": {
		"speaker": "Athena",
		"text": "The sacred shrine of Delphi has been desecrated by Roman pillagers. Purge the defilers, Nikolaos, and awaken the Golden Aegis!",
		"color": Color(1.0, 0.85, 0.25)
	},
	"athena_level8_delos": {
		"speaker": "Athena",
		"text": "The Isle of Delos! Seize their fleet of warships and liberate our trapped archers. Today, Greece takes the war to Roman shores!",
		"color": Color(1.0, 0.85, 0.25)
	},
	"athena_level9_appian_way": {
		"speaker": "Athena",
		"text": "We march upon the Appian Way! Roman catapults and ballistas guard the road to Rome. Charge through their camps and smash their legions!",
		"color": Color(1.0, 0.85, 0.25)
	},
	"athena_level10_rome_colosseum": {
		"speaker": "Athena",
		"text": "The Colosseum of Rome! Face Supreme Consul Titus Claudius and his Praetorian guard! End this tyranny and crown Hellas in eternal triumph!",
		"color": Color(1.0, 0.85, 0.25)
	},
	"athena_low_health": {
		"speaker": "Athena",
		"text": "Stand strong, warrior! Do not falter now. Commune with the Gods and regain your vigor!",
		"color": Color(1.0, 0.85, 0.25)
	},
	"athena_victory": {
		"speaker": "Athena",
		"text": "Hellas is restored! Your courage and strategy have echoed into eternity. Olympus honors you, Champion of Greece!",
		"color": Color(1.0, 0.85, 0.25)
	},
	"athena_tactical_advice": {
		"speaker": "Athena",
		"text": "Keep moving, warrior! Time your dodges and use the terrain to flank their shields.",
		"color": Color(1.0, 0.85, 0.25)
	}
}

func _ready():
	process_mode = Node.PROCESS_MODE_ALWAYS
	# Sound effects
	_load_sound("sword_swing", "res://assets/audio/sword_swing.wav")
	_load_sound("campaign_intro_2", "res://assets/audio/campaign_victory.wav")
	_load_sound("campaign_intro_3", "res://assets/audio/war_horn_roman.wav")
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
	_load_sound("campaign_victory", "res://assets/audio/campaign_victory.wav")

	# Expanded SFX
	_load_sound("arrow_shoot", "res://assets/audio/arrow_shoot.wav")
	_load_sound("arrow_hit", "res://assets/audio/arrow_hit.wav")
	_load_sound("horse_gallop", "res://assets/audio/horse_gallop.wav")
	_load_sound("horse_neigh", "res://assets/audio/horse_neigh.wav")
	_load_sound("lance_pierce", "res://assets/audio/lance_pierce.wav")
	_load_sound("minotaur_slam", "res://assets/audio/minotaur_slam.wav")

	# Expanded Dialogues
	_load_sound("zeus_manifest", "res://assets/audio/zeus_manifest.wav")
	_load_sound("poseidon_manifest", "res://assets/audio/poseidon_manifest.wav")
	_load_sound("hades_manifest", "res://assets/audio/hades_manifest.wav")
	_load_sound("ares_manifest", "res://assets/audio/ares_manifest.wav")
	_load_sound("archer_select", "res://assets/audio/archer_select.wav")
	_load_sound("archer_shoot", "res://assets/audio/archer_shoot.wav")
	_load_sound("cavalry_select", "res://assets/audio/cavalry_select.wav")
	_load_sound("cavalry_charge", "res://assets/audio/cavalry_charge.wav")
	_load_sound("roman_archer_shout", "res://assets/audio/roman_archer_shout.wav")
	_load_sound("roman_cavalry_charge", "res://assets/audio/roman_cavalry_charge.wav")
	_load_sound("minotaur_bellow", "res://assets/audio/minotaur_bellow.wav")
	_load_sound("biome_coast", "res://assets/audio/biome_coast.wav")
	_load_sound("biome_chasm", "res://assets/audio/biome_chasm.wav")

	# Athena Commentary (Sudha Devarakonda - ElevenLabs v4)
	_load_sound("athena_intro", "res://assets/audio/athena_intro.wav")
	_load_sound("athena_pray_zeus", "res://assets/audio/athena_pray_zeus.wav")
	_load_sound("athena_pray_poseidon", "res://assets/audio/athena_pray_poseidon.wav")
	_load_sound("athena_pray_hades", "res://assets/audio/athena_pray_hades.wav")
	_load_sound("athena_pray_ares", "res://assets/audio/athena_pray_ares.wav")
	_load_sound("athena_class_archer", "res://assets/audio/athena_class_archer.wav")
	_load_sound("athena_class_cavalry", "res://assets/audio/athena_class_cavalry.wav")
	_load_sound("athena_class_champion", "res://assets/audio/athena_class_champion.wav")
	_load_sound("athena_level2_coast", "res://assets/audio/athena_level2_coast.wav")
	_load_sound("athena_level3_valley", "res://assets/audio/athena_level3_valley.wav")
	_load_sound("athena_army_assembled", "res://assets/audio/athena_army_assembled.wav")
	_load_sound("athena_level4_chasm", "res://assets/audio/athena_level4_chasm.wav")
	_load_sound("athena_level5_siege", "res://assets/audio/athena_level5_siege.wav")
	_load_sound("athena_level6_thermopylae", "res://assets/audio/athena_level6_thermopylae.wav")
	_load_sound("athena_level7_delphi", "res://assets/audio/athena_level7_delphi.wav")
	_load_sound("athena_level8_delos", "res://assets/audio/athena_level8_delos.wav")
	_load_sound("athena_level9_appian_way", "res://assets/audio/athena_level9_appian_way.wav")
	_load_sound("athena_level10_rome_colosseum", "res://assets/audio/athena_level10_rome_colosseum.wav")
	_load_sound("athena_low_health", "res://assets/audio/athena_low_health.wav")
	_load_sound("athena_victory", "res://assets/audio/athena_victory.wav")
	_load_sound("athena_tactical_advice", "res://assets/audio/athena_tactical_advice.wav")

	# Create SFX player pool
	for i in range(pool_size):
		var p = AudioStreamPlayer.new()
		add_child(p)
		players.append(p)

	# Dedicated Dialogue player
	dialogue_player = AudioStreamPlayer.new()
	dialogue_player.volume_db = 4.0
	add_child(dialogue_player)

	# Dedicated Athena player (Sudha Devarakonda)
	athena_player = AudioStreamPlayer.new()
	athena_player.volume_db = 5.5
	add_child(athena_player)

	# Background Ambience / Music player
	music_player = AudioStreamPlayer.new()
	music_player.volume_db = -8.0
	add_child(music_player)
	_start_bgm()

func _start_bgm():
	if sounds.has("prayer"):
		music_player.stream = sounds["prayer"]
		music_player.play()
		music_player.finished.connect(func():
			if music_player:
				music_player.play()
		)

func _load_sound(sound_name: String, path: String):
	var s = load(path)
	if s:
		sounds[sound_name] = s
	elif ResourceLoader.exists(path):
		sounds[sound_name] = ResourceLoader.load(path)
	elif FileAccess.file_exists(path):
		sounds[sound_name] = load(path)

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

func play_athena(key: String, force: bool = false):
	if not sounds.has(key):
		return

	var stream = sounds[key]
	athena_player.stream = stream
	athena_player.pitch_scale = 1.0
	athena_player.play()

	if dialogues.has(key):
		var info = dialogues[key]
		var dur = 4.0
		if stream is AudioStream:
			dur = max(3.0, stream.get_length())
		emit_signal("dialogue_started", info["speaker"], info["text"], info["color"], dur)

func stop_all_dialogues():
	if dialogue_player and dialogue_player.playing:
		dialogue_player.stop()
	if athena_player and athena_player.playing:
		athena_player.stop()
	last_dialogue_time = -100.0
