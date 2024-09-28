@tool
extends ItemList

var folders := []
var files := []

func _can_drop_data(_position, data) -> bool:
	return data as Dictionary and data.has('files')

const folder_prefix := 'dir:  '
const file_prefix   := 'file: '

func _drop_data(position, data) -> void:
	var paths : Array = data.files
	for path : String in paths.filter( func(p : String): return (
		# avoid duplicates
		( p.ends_with('.gd') and p not in files ) \
		or (p.ends_with('/') and p not in folders )
		) ):
		# NOTE : there can be duplicates by adding files that are in a selected folder,
		# but transpiler takes care of it
		
		var is_folder := path.ends_with('/')
		var list : Array = folders if is_folder else files
		list.append( path )
		
		var displayed_name = path.replace('res://', '')
		displayed_name = folder_prefix + displayed_name.left(-1) if is_folder \
		  else file_prefix + displayed_name
		
		var index := get_item_count()
		add_item( displayed_name )
		set_item_metadata(index, path)
		set_item_tooltip(index, path + '\n(double-click to remove)')

func _ready():
	self.item_activated.connect(_on_remove_item)

func _on_remove_item(i:int) -> void:
	var path : String = get_item_metadata(i)
	folders.erase(path)
	files.erase(path)
	remove_item(i)
	
func _input(event):
	# prevent enter key from triggering ListItem's item_activated signal
	if event.is_action("ui_accept") and self.has_focus():
		get_viewport().set_input_as_handled()
