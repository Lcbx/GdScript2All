@tool
extends EditorPlugin

const UI_scene := 'res://addons/gdscript2all/script_converter_UI.tscn'

var UI : Control

func _enter_tree():
	UI = load(UI_scene).instantiate()
	add_control_to_bottom_panel(UI, 'GdScript Converter')
	make_bottom_panel_item_visible(UI)

func _exit_tree():
	remove_control_from_bottom_panel(UI)
