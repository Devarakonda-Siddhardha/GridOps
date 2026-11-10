extends Control

@onready var close_button = $Panel/VBox/Header/CloseButton
@onready var title_label = $Panel/VBox/Header/Title

func _ready():
	visible = false
	process_mode = Node.PROCESS_MODE_ALWAYS
	if close_button:
		close_button.pressed.connect(close_codex)
	CampaignManager.codex_toggled.connect(toggle_codex)

func toggle_codex():
	if visible:
		close_codex()
	else:
		open_codex()

func open_codex():
	visible = true
	get_tree().paused = true
	Input.set_mouse_mode(Input.MOUSE_MODE_VISIBLE)
	SoundManager.play("prayer_chant", 1.0, -2.0)

func close_codex():
	visible = false
	get_tree().paused = false
	Input.set_mouse_mode(Input.MOUSE_MODE_CAPTURED)

func _input(event):
	if visible and event is InputEventKey and event.is_pressed() and not event.is_echo():
		if event.keycode == KEY_ESCAPE or event.keycode == KEY_B or event.keycode == KEY_P:
			close_codex()
			get_viewport().set_input_as_handled()
