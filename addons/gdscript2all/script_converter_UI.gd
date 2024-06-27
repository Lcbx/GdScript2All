@tool
extends Control

const transpiler_path := "res://addons/gdscript2all/converter/"

# dummy radiobutton used to get ButtonGroup
# NOTE : language buttons must have 'transpiler_name' metadata (and the same ButtonGroup as the others)
@onready var button_group : CheckBox = $Controls/languages/ButtonGroup

@onready var script_itemlist :ItemList = $scripts/items
@onready var output_edit : TextEdit = $Controls/output/Edit
@onready var logs = $Controls/logs/content

# crashes
#var thread := Thread.new()

func _generate_scripts_pressed():
	logs.text = ''
	
	# get all paths
	var script_paths : Array = (script_itemlist.folders + script_itemlist.files) \
	  .map(func(path): return ProjectSettings.globalize_path(path) )
	
	var language_button : Button = (button_group.button_group as ButtonGroup).get_pressed_button()
	var transpiler : String = language_button.get_meta('transpiler_name')
	
	var output_folder := output_edit.text if output_edit.text else 'res://' + transpiler
	output_folder = ProjectSettings.globalize_path(output_folder)
	
	var transpiler_path = ProjectSettings.globalize_path(transpiler_path)
	var exe_name := 'main.exe' if OS.get_name() == 'Windows' else 'main'
	var output := []
	var command := ( script_paths
		+ [ '-t', transpiler ]
		+ [ '-o', output_folder ]
		)
	
	logs.text += 'command : %s\n\n' % [' '.join(command)] 
	var task = OS.execute.bind(transpiler_path + exe_name,command,output, true)
	task.call()
	
	#thread.start(task)
	#tree_exiting.connect(thread.wait_to_finish)
	#while thread.is_alive():
	#	await get_tree().process_frame
	#thread.wait_to_finish()
	#tree_exiting.disconnect(thread.wait_to_finish)
	
	logs.text += output[0]
