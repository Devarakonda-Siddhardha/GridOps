extends StaticBody3D

signal gate_destroyed

var health: float = 250.0
var is_broken: bool = false

@onready var prompt_label = $PromptLabel
@onready var model = $Model

func _ready():
	add_to_group("destructible")
	if prompt_label:
		prompt_label.text = "⚔ CASTRUM FORTRESS GATE ⚔\n(Breach the Gate to reach General Marcus!)"

func take_damage(amount: float, knockback: Vector3 = Vector3.ZERO, damage_type: String = "melee"):
	if is_broken:
		return

	health -= amount
	SoundManager.play("sword_hit", 0.7)

	if prompt_label:
		prompt_label.text = "⚔ Fortress Gate: %d / 250 HP ⚔" % int(max(0, health))

	if health <= 0.0:
		_breach_gate()

func _breach_gate():
	is_broken = true
	SoundManager.play("gate_smash", 1.0)
	if prompt_label:
		prompt_label.visible = false

	DivineManager.emit_signal("message_broadcast", "FORTRESS GATE BREACHED!", "The path to General Marcus is open! CHARGE!")
	AthenaCommentary.trigger_fortress_gate()
	emit_signal("gate_destroyed")

	$CollisionShape3D.set_deferred("disabled", true)
	if model:
		var tween = create_tween()
		tween.tween_property(model, "position:y", model.position.y - 6.0, 1.2)
		tween.tween_callback(queue_free)
	else:
		queue_free()
