@tool class_name gdscript2all_plugin extends EditorPlugin

const UI_scene := 'res://addons/gdscript2all/script_converter_UI.tscn'
var UI : Control

func _enter_tree():
	UI = load(UI_scene).instantiate()
	add_control_to_bottom_panel(UI, 'GdScript Converter')
	setup_settings()

func _exit_tree():
	remove_control_from_bottom_panel(UI)

# addon settings

const settings_path := 'docks/gdscript2all/'
const display_command := settings_path + 'display_exe_command'

func setup_settings():
	if not EditorInterface.get_editor_settings().has_setting(display_command):
		EditorInterface.get_editor_settings().set_setting(display_command, false)
		make_bottom_panel_item_visible(UI)
