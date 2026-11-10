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
	is_mobile = OS.get_name() == "Android" or DisplayServer.is_touchscreen_available()
	if not is_mobile:
		Input.set_mouse_mode(Input.MOUSE_MODE_CAPTURED)
	else:
		Input.set_mouse_mode(Input.MOUSE_MODE_VISIBLE)

func _unhandled_input(event):
	if not is_mobile:
		if event is InputEventMouseButton and event.pressed and event.button_index == MOUSE_BUTTON_LEFT:
			if not is_mouse_captured:
				Input.set_mouse_mode(Input.MOUSE_MODE_CAPTURED)
				is_mouse_captured = true

		if event.is_action_pressed("pause"):
			is_mouse_captured = not is_mouse_captured
			Input.set_mouse_mode(Input.MOUSE_MODE_CAPTURED if is_mouse_captured else Input.MOUSE_MODE_VISIBLE)

		if is_mouse_captured and event is InputEventMouseMotion:
			yaw -= event.relative.x * mouse_sensitivity
			pitch = clamp(pitch - event.relative.y * mouse_sensitivity * 50.0, min_pitch, max_pitch)
			rotation.y = yaw
			if spring_arm:
				spring_arm.rotation_degrees.x = pitch
	else:
		if event is InputEventScreenDrag:
			# Swiping right 65% of screen rotates camera
			if event.position.x > get_viewport().get_visible_rect().size.x * 0.35:
				yaw -= event.relative.x * mouse_sensitivity * 1.6
				pitch = clamp(pitch - event.relative.y * mouse_sensitivity * 60.0, min_pitch, max_pitch)
				rotation.y = yaw
				if spring_arm:
					spring_arm.rotation_degrees.x = pitch

func get_camera_basis() -> Basis:
	return Basis(Vector3.UP, yaw)
