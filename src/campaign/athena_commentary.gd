extends Node

var last_commentary_time: float = -30.0
var commentary_cooldown: float = 6.0
var low_health_warning_cooldown: float = 35.0
var last_low_health_time: float = -50.0

var voiced_classes = {
	"warrior": "athena_class_champion",
	"archer": "athena_class_archer",
	"cavalry": "athena_class_cavalry"
}

var god_prayers = {
	"zeus": "athena_pray_zeus",
	"poseidon": "athena_pray_poseidon",
	"hades": "athena_pray_hades",
	"ares": "athena_pray_ares"
}

func _ready():
	process_mode = Node.PROCESS_MODE_ALWAYS
	CampaignManager.hero_class_changed.connect(_on_hero_class_changed)
	CampaignManager.army_changed.connect(_on_army_changed)
	DivineManager.power_unlocked.connect(_on_power_unlocked)

func play_athena(key: String, force: bool = false):
	var current_time = Time.get_ticks_msec() / 1000.0
	if not force and (current_time - last_commentary_time) < commentary_cooldown:
		return
	last_commentary_time = current_time
	SoundManager.play_athena(key, force)

func _on_hero_class_changed(new_class: String):
	if voiced_classes.has(new_class):
		get_tree().create_timer(0.8).timeout.connect(func():
			play_athena(voiced_classes[new_class])
		)

func _on_power_unlocked(god_id: String):
	if god_prayers.has(god_id):
		get_tree().create_timer(3.2).timeout.connect(func():
			play_athena(god_prayers[god_id])
		)

func _on_army_changed(count: int, _max_val: int):
	if count > 0 and count % 4 == 0:
		get_tree().create_timer(1.2).timeout.connect(func():
			play_athena("athena_army_assembled")
		)

func check_player_health(current: float, max_val: float):
	var ratio = current / max(1.0, max_val)
	var current_time = Time.get_ticks_msec() / 1000.0
	if ratio < 0.35 and (current_time - last_low_health_time) > low_health_warning_cooldown:
		last_low_health_time = current_time
		play_athena("athena_low_health", true)
