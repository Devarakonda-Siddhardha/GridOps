extends Node3D

@export var god_id: String = "zeus"
@export var title: String = "Zeus, King of Olympus"

var has_manifested: bool = false
var is_player_near: bool = false
var anim_player: AnimationPlayer = null

const GOD_MODELS = {
	"zeus": "res://assets/models/sf_god_zeus.glb",
	"poseidon": "res://assets/models/sf_god_poseidon.glb",
	"hades": "res://assets/models/sf_god_hades.glb",
	"ares": "res://assets/models/sf_god_ares.glb",
	"athena": "res://assets/models/sf_god_athena.glb"
}

const GOD_COLORS = {
	"zeus": Color(0.4, 0.85, 1.0),
	"poseidon": Color(0.2, 0.95, 0.85),
	"hades": Color(0.75, 0.35, 1.0),
	"ares": Color(1.0, 0.25, 0.15),
	"athena": Color(1.0, 0.85, 0.25)
}

@onready var light: OmniLight3D = $OmniLight3D
@onready var title_label: Label3D = $TitleLabel
@onready var interact_label: Label3D = $InteractLabel
@onready var model_pivot: Node3D = $ModelPivot

func _ready():
	add_to_group("gods")
	if title_label:
		title_label.text = title
	if light and GOD_COLORS.has(god_id):
		light.light_color = GOD_COLORS[god_id]
	if interact_label:
		interact_label.visible = false

	# Instantiate Sketchfab God Statue dynamically via AutoFit
	if GOD_MODELS.has(god_id) and ResourceLoader.exists(GOD_MODELS[god_id]):
		var af = AutoFit.new()
		af.target_size = 3.6
		af.fit_axis = "y"
		if god_id == "hades":
			af.tint = Color(0.72, 0.55, 0.95, 1.0)
		elif god_id == "ares":
			af.tint = Color(1.0, 0.65, 0.55, 1.0)
		model_pivot.add_child(af)
		af.load_model(GOD_MODELS[god_id])

	$ProximityArea.body_entered.connect(_on_body_entered)
	$ProximityArea.body_exited.connect(_on_body_exited)

func _process(_delta):
	if is_player_near and (Input.is_action_just_pressed("interact_pray") or (InputMap.has_action("interact") and Input.is_action_just_pressed("interact"))):
		_commune_with_god()

func _on_body_entered(body: Node3D):
	if body.is_in_group("player"):
		is_player_near = true
		if interact_label:
			interact_label.visible = true

		if not has_manifested:
			has_manifested = true
			if anim_player and anim_player.has_animation("Bless"):
				anim_player.play("Bless")
			if god_id == "athena":
				SoundManager.play_dialogue("athena_intro", true)
				DivineManager.emit_signal("message_broadcast", "🦉 ATHENA'S GUIDANCE", "The Goddess of Wisdom guides your path to victory!")
			else:
				SoundManager.play_dialogue("%s_manifest" % god_id)
				DivineManager.unlock_power(god_id)
				DivineManager.emit_signal("message_broadcast", "%s HAS SPOKEN!" % god_id.to_upper(), "Received the blessing of %s!" % title)

func _on_body_exited(body: Node3D):
	if body.is_in_group("player"):
		is_player_near = false
		if interact_label:
			interact_label.visible = false
		if anim_player and anim_player.has_animation("Idle"):
			anim_player.play("Idle")

func _commune_with_god():
	if anim_player and anim_player.has_animation("Cast"):
		anim_player.play("Cast")
	var player = get_tree().get_first_node_in_group("player")
	if player and player.has_method("heal"):
		player.heal(100.0)
	SoundManager.play("prayer", 1.0)
	DivineManager.emit_signal("message_broadcast", "DIVINE SANCTUARY", "%s restores your vitality!" % title)
