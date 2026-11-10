extends Node3D

@export_enum("zeus", "poseidon", "hades", "ares") var god: String = "zeus"
@export var altar_title: String = "Altar of the Gods"

var player_in_range: bool = false
var is_attuned: bool = false
var pray_time: float = 0.0
var pray_duration: float = 1.3

@onready var beam = $DivineBeam
@onready var prompt_label = $PromptLabel
@onready var model_slot = $ModelSlot

func _ready():
	_load_god_model()
	if prompt_label:
		prompt_label.visible = false

func _load_god_model():
	var glb_path = "res://assets/models/altar_%s.glb" % god
	if ResourceLoader.exists(glb_path):
		var packed = load(glb_path)
		if packed:
			var inst = packed.instantiate()
			model_slot.add_child(inst)

func _process(delta):
	if is_attuned:
		if prompt_label:
			prompt_label.visible = false
		return

	if player_in_range:
		var player = get_tree().get_first_node_in_group("player")
		if player and Input.is_action_pressed("interact_pray") and not player.is_dead:
			pray_time += delta
			player.start_praying(god)
			var pct = clamp(pray_time / pray_duration, 0.0, 1.0)
			if prompt_label:
				prompt_label.text = "Praying to %s... %d%%" % [god.capitalize(), int(pct * 100)]
				prompt_label.visible = true

			if pray_time >= pray_duration:
				_complete_prayer()
		else:
			pray_time = max(0.0, pray_time - delta * 2.0)
			if prompt_label:
				prompt_label.text = "[E] Pray to " + god.capitalize()
				prompt_label.visible = true
	else:
		pray_time = 0.0
		if prompt_label:
			prompt_label.visible = false

func _complete_prayer():
	is_attuned = true
	DivineManager.unlock_blessing(god)
	SoundManager.play("prayer", 1.0, 3.0)
	SoundManager.play_dialogue("god_" + god + "_blessing", true)
	if beam:
		beam.visible = true
	if prompt_label:
		prompt_label.text = "Blessed by " + god.capitalize()
		prompt_label.modulate = Color(1.0, 0.85, 0.2)

func _on_prayer_area_body_entered(body):
	if body.is_in_group("player"):
		player_in_range = true

func _on_prayer_area_body_exited(body):
	if body.is_in_group("player"):
		player_in_range = false
		var player = get_tree().get_first_node_in_group("player")
		if player:
			player.stop_praying()
