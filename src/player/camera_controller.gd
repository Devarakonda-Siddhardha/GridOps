extends Node3D

@export var mouse_sensitivity: float = 0.003
@export var min_pitch: float = -60.0
@export var max_pitch: float = 25.0

@onready var spring_arm = $SpringArm3D
@onready var camera = $SpringArm3D/Camera3D

var pitch: float = -15.0
var yaw: float = 0.0
var is_mouse_captured: bool = true
var target: Node3D = null
var is_mobile: bool = false

func _ready():
	is_mobile = OS.get_name() == "Android" or OS.get_name() == "iOS"
	yaw = rotation.y
	if spring_arm:
		spring_arm.rotation_degrees.x = pitch
	if not is_mobile:
		Input.set_mouse_mode(Input.MOUSE_MODE_CAPTURED)
		is_mouse_captured = true
	else:
		Input.set_mouse_mode(Input.MOUSE_MODE_VISIBLE)
		is_mouse_captured = false

func _input(event):
	if not is_mobile:
		if event.is_action_pressed("pause"):
			is_mouse_captured = not is_mouse_captured
			Input.set_mouse_mode(Input.MOUSE_MODE_CAPTURED if is_mouse_captured else Input.MOUSE_MODE_VISIBLE)
			return

		if event is InputEventMouseButton and event.pressed and event.button_index == MOUSE_BUTTON_LEFT:
			if not is_mouse_captured and Input.get_mouse_mode() != Input.MOUSE_MODE_CAPTURED:
				# Only recapture if no UI modal/victory/gameover panel is visible
				var hud = get_tree().get_first_node_in_group("hud")
				var ui_blocking = false
				if hud:
					var vp = hud.get_node_or_null("VictoryPanel")
					var go = hud.get_node_or_null("GameOverPanel")
					if (vp and vp.visible) or (go and go.visible):
						ui_blocking = true
				if not ui_blocking:
					Input.set_mouse_mode(Input.MOUSE_MODE_CAPTURED)
					is_mouse_captured = true
					return

		if is_mouse_captured and event is InputEventMouseMotion:
			yaw = wrapf(yaw - event.relative.x * mouse_sensitivity, -PI, PI)
			pitch = clamp(pitch - event.relative.y * mouse_sensitivity * 50.0, min_pitch, max_pitch)
			rotation.y = yaw
			if spring_arm:
				spring_arm.rotation_degrees.x = pitch
	else:
		if event is InputEventScreenDrag:
			# Swiping right 65% of screen rotates camera
			if event.position.x > get_viewport().get_visible_rect().size.x * 0.35:
				yaw = wrapf(yaw - event.relative.x * mouse_sensitivity * 1.6, -PI, PI)
				pitch = clamp(pitch - event.relative.y * mouse_sensitivity * 60.0, min_pitch, max_pitch)
				rotation.y = yaw
				if spring_arm:
					spring_arm.rotation_degrees.x = pitch

func get_camera_basis() -> Basis:
	return Basis(Vector3.UP, yaw)
