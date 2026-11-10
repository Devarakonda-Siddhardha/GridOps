extends StaticBody3D

@export var captive_count: int = 3
var health: float = 80.0
var is_broken: bool = false

@onready var prompt_label = $PromptLabel
@onready var model = $Model

func _ready():
	add_to_group("destructible")
	if prompt_label:
		prompt_label.text = "🔒 Captured Greek Hoplites\n(Attack cage to liberate)"

func take_damage(amount: float, knockback: Vector3 = Vector3.ZERO, damage_type: String = "melee"):
	if is_broken:
		return

	health -= amount
	SoundManager.play("sword_hit", 0.8)

	if prompt_label:
		prompt_label.text = "🔒 Cage Health: %d HP" % int(max(0, health))

	if health <= 0.0:
		_break_cage()

func _break_cage():
	is_broken = true
	SoundManager.play("cage_break", 1.0)
	if prompt_label:
		prompt_label.visible = false

	# Spawn Greek allies
	var soldier_scene = load("res://src/allies/greek_soldier.tscn")
	var root = get_tree().current_scene

	for i in range(captive_count):
		var s = soldier_scene.instantiate()
		s.squad_index = CampaignManager.army_count + i
		root.add_child(s)
		s.global_position = global_position + Vector3(randf_range(-1.5, 1.5), 0, randf_range(-1.5, 1.5))

	CampaignManager.recruit_allies(captive_count)
	CampaignManager.rescued_cages += 1
	DivineManager.emit_signal("message_broadcast", "CAPTIVES FREED!", "+%d Greek Hoplites joined your Army! (%d/%d Camps)" % [captive_count, CampaignManager.rescued_cages, CampaignManager.total_cages])

	$CollisionShape3D.set_deferred("disabled", true)
	if model:
		var tween = create_tween()
		tween.tween_property(model, "scale", Vector3(0.01, 0.01, 0.01), 0.3)
		tween.tween_callback(queue_free)
	else:
		queue_free()
