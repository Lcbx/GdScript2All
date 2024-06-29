@tool extends Control

const transpiler_localpath := "res://addons/gdscript2all/converter/"
const logs_localpath := "user://gdscript2all_logs.txt"

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
	  .map(func(path): return ProjectSettings.globalize_path(path) )
	
	var transpiler_name := get_transpiler_name()
	
	var output_path := 'res://' + (output_edit.text if output_edit.text else transpiler_name)
	var output_folder := ProjectSettings.globalize_path(output_path)
	var logs_path := ProjectSettings.globalize_path(logs_localpath)
	
	var exe_name := 'main.exe' if OS.get_name() == 'Windows' else 'main'
	var transpiler_exe_path := ProjectSettings.globalize_path(transpiler_localpath) + exe_name
	
	var output := []
	var command := ( script_paths
		+ [ '-t', transpiler_name ]
		+ [ '-o', output_folder ]
		+ [ '--log_file', logs_path ]
		)
	
	if EditorInterface.get_editor_settings().get_setting(gdscript2all_plugin.display_command):
		logs.text += 'command : %s %s\n\n' % [ transpiler_exe_path, ' '.join(command)]
	
	var pid = OS.create_process(transpiler_exe_path, command)
	
	var timeout_s : float = EditorInterface.get_editor_settings().get_setting(gdscript2all_plugin.timeout_setting)
	get_tree().create_timer(timeout_s).timeout.connect(_on_execution_timeout.bind(pid))
	
	while OS.is_process_running(pid):
		await get_tree().process_frame
	
	logs.text += FileAccess.open(logs_path, FileAccess.READ).get_as_text()


func get_transpiler_name() -> String:
	return button_group.button_group.get_pressed_button().get_meta('transpiler_name') as String

func _on_toggled(toggled_on):
	output_edit.placeholder_text = 'res://' + get_transpiler_name()

func _on_execution_timeout(pid:int):
	if OS.is_process_running(pid):
		OS.kill(pid)
		logs.text += 'execution timeout, you can set a longer time in %s' %  [gdscript2all_plugin.timeout_setting]

