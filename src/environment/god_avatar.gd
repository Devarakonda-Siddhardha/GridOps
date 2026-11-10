extends Node3D

@export var god_id: String = "zeus"
@export var title: String = "Zeus, King of Olympus"

var has_manifested: bool = false
var is_player_near: bool = false
var anim_player: AnimationPlayer = null

const GOD_MODELS = {
	"zeus": "res://assets/models/god_zeus.glb",
	"poseidon": "res://assets/models/god_poseidon.glb",
	"hades": "res://assets/models/god_hades.glb",
	"ares": "res://assets/models/god_ares.glb"
}

const GOD_COLORS = {
	"zeus": Color(0.4, 0.85, 1.0),
	"poseidon": Color(0.2, 0.95, 0.85),
	"hades": Color(0.75, 0.35, 1.0),
	"ares": Color(1.0, 0.25, 0.15)
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

	# Instantiate God Model dynamically
	if GOD_MODELS.has(god_id) and ResourceLoader.exists(GOD_MODELS[god_id]):
		var packed_model = load(GOD_MODELS[god_id])
		if packed_model:
			var m_inst = packed_model.instantiate()
			model_pivot.add_child(m_inst)
			anim_player = m_inst.get_node_or_null("AnimationPlayer")
			if anim_player and anim_player.has_animation("Idle"):
				anim_player.play("Idle")

	$ProximityArea.body_entered.connect(_on_body_entered)
	$ProximityArea.body_exited.connect(_on_body_exited)

func _process(_delta):
	if is_player_near and Input.is_action_just_pressed("interact"):
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
