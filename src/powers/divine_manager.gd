extends Node

signal power_unlocked(god_name)
signal cooldown_updated(god_name, remaining, max_cd)
signal message_broadcast(title, subtitle)
signal boss_spawned(boss_name, max_hp)
signal boss_health_updated(current, max_val)
signal boss_defeated()
signal camera_shake_requested(intensity, duration)

var powers = {
	"zeus": {
		"name": "Zeus",
		"title": "Wrath of Olympus",
		"desc": "Call down thunder to smite demons with lethal chain lightning.",
		"color": Color(0.3, 0.7, 1.0),
		"unlocked": false,
		"cooldown": 5.0,
		"timer": 0.0,
		"key": "1 / Q",
		"scene": preload("res://src/powers/lightning_strike.tscn")
	},
	"poseidon": {
		"name": "Poseidon",
		"title": "Tidal Cataclysm",
		"desc": "Unleash a crushing ocean wave that knocks enemies back.",
		"color": Color(0.1, 0.9, 0.8),
		"unlocked": false,
		"cooldown": 6.5,
		"timer": 0.0,
		"key": "2 / F",
		"scene": preload("res://src/powers/tidal_wave.tscn")
	},
	"hades": {
		"name": "Hades",
		"title": "Soul Leech",
		"desc": "Drain the life essence of surrounding demons to heal your wounds.",
		"color": Color(0.7, 0.1, 0.95),
		"unlocked": false,
		"cooldown": 7.5,
		"timer": 0.0,
		"key": "3 / R",
		"scene": preload("res://src/powers/soul_drain.tscn")
	},
	"ares": {
		"name": "Ares",
		"title": "Bloodlust of War",
		"desc": "Explode with battle fury, stunning demons and gaining +150% attack power.",
		"color": Color(1.0, 0.15, 0.05),
		"unlocked": false,
		"cooldown": 10.0,
		"timer": 0.0,
		"key": "4 / C",
		"scene": preload("res://src/powers/ares_fury.tscn")
	}
}

func _process(delta):
	for god in powers.keys():
		if powers[god]["timer"] > 0.0:
			powers[god]["timer"] = max(0.0, powers[god]["timer"] - delta)
			emit_signal("cooldown_updated", god, powers[god]["timer"], powers[god]["cooldown"])

func unlock_blessing(god: String):
	if powers.has(god):
		powers[god]["unlocked"] = true
		emit_signal("power_unlocked", god)
		emit_signal("message_broadcast", "BLESSING OF " + god.to_upper() + " GRANTED!", powers[god]["title"])

func can_cast(god: String) -> bool:
	if not powers.has(god):
		return false
	return powers[god]["unlocked"] and powers[god]["timer"] <= 0.0

func cast_power(god: String, origin: Vector3 = Vector3.ZERO, forward_dir: Vector3 = Vector3.ZERO) -> bool:
	if not can_cast(god):
		return false

	var p = get_tree().get_first_node_in_group("player")
	if origin == Vector3.ZERO and p:
		origin = p.global_position
		forward_dir = -p.transform.basis.z
	elif forward_dir == Vector3.ZERO:
		forward_dir = Vector3.FORWARD

	var info = powers[god]
	info["timer"] = info["cooldown"]

	var power_inst = info["scene"].instantiate()
	var root = get_tree().current_scene
	root.add_child(power_inst)

	if god == "zeus":
		var target_pos = origin + forward_dir * 8.0
		var enemies = get_tree().get_nodes_in_group("enemies")
		var nearest = null
		var min_d = 16.0
		for e in enemies:
			if is_instance_valid(e):
				var d = origin.distance_to(e.global_position)
				if d < min_d:
					min_d = d
					nearest = e
		if nearest:
			target_pos = nearest.global_position
		target_pos.y = 0.0
		power_inst.global_position = target_pos
		power_inst.activate()
		SoundManager.play("lightning", 1.0, 3.0)
		SoundManager.play_dialogue("god_zeus_cast", true)

	elif god == "poseidon":
		power_inst.global_position = origin + forward_dir * 1.5 + Vector3.UP * 0.1
		power_inst.setup(forward_dir)
		SoundManager.play("water_wave", 1.0, 2.0)
		SoundManager.play_dialogue("god_poseidon_cast", true)

	elif god == "hades":
		power_inst.global_position = origin + Vector3.UP * 0.05
		power_inst.activate()
		SoundManager.play("soul_drain", 1.0, 2.0)
		SoundManager.play_dialogue("god_hades_cast", true)

	elif god == "ares":
		power_inst.global_position = origin + Vector3.UP * 0.2
		power_inst.activate()
		SoundManager.play("ares_fury", 1.0, 3.0)
		SoundManager.play_dialogue("god_ares_cast", true)

	emit_signal("cooldown_updated", god, info["timer"], info["cooldown"])
	AthenaCommentary.trigger_divine_cast()
	return true
