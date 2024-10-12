@tool extends Control

const transpiler_path := "./addons/gdscript2all/converter/"

# dummy radiobutton used to get ButtonGroup
# NOTE : language buttons must have 'transpiler_name' metadata (and the same ButtonGroup as the others)
@onready var button_group : CheckBox = $Controls/languages/ButtonGroup

@onready var script_itemlist :ItemList = $scripts/items
@onready var output_edit : TextEdit = $Controls/output/Edit
@onready var logs = $Controls/logs/content

func _generate_scripts_pressed():
	logs.text = ''
	
	# get all paths
	var script_paths : Array = (script_itemlist.folders + script_itemlist.files) \
	  .map(func(path): return path.replace("res://", "./") )
	
	var transpiler_name := get_transpiler_name()
	
	var output_path := './' + (output_edit.text if output_edit.text else transpiler_name).replace("res://", "")
	
	var command := ( [
		transpiler_path + 'main.py'
		] + script_paths + [
		'-t', transpiler_name,
		'-o', output_path
		] )
	
	if EditorInterface.get_editor_settings().get_setting(gdscript2all_plugin.display_command):
		logs.text += 'command : %s\n\n' % [ ' '.join(command) ]
	
	var output := []
	OS.execute("python", command, output, true, false)
		
	logs.text += ''.join( output.map( \
		func(s): return s.replace('[91m', '[b]').replace('[0m', '[/b]')\
		))


func get_transpiler_name() -> String:
	return button_group.button_group.get_pressed_button().get_meta('transpiler_name') as String

func _on_toggled(toggled_on):
	output_edit.placeholder_text = 'res://' + get_transpiler_name()
