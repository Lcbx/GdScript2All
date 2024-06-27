extends ResourceFormatSaver

# tried an approach where we would 'save as' gdscript scripts into a csharp / cpp file
# but Godot does not support that rn

func register() -> void:
	ResourceSaver.add_resource_format_saver(self)

func _get_recognized_extensions(resource: Resource) -> PackedStringArray:
	print('_get_recognized_extensions')
	return PackedStringArray(['csharp', 'cpp'])

func _recognize(resource: Resource) -> bool:
	print('_recognize')
	return resource is GDScript

func _recognize_path(resource: Resource, path: String) -> bool:
	print('_recognize_path')
	return resource is GDScript

func _save(resource: Resource, path: String, flags: int) -> Error:
	print('_save')
	return OK

#func _set_uid(path: String, uid: int) -> Error:
#	return OK

