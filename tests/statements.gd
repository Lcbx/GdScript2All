extends Node

# method to test statements
func method():
	
	pass
	
	var i = 0
	
	if true:
		assert(false)
	elif false:
		convert("Hello"+" "+"World", TYPE_STRING)
	elif true:
		print("Goodbye ", "World")
	else:
		print(get_stack())
	
	while false:
		i += 1
		break
		continue
	
	for j in range(i):
		i += j

	for j in array:
		i += j

	if i is int: i = 0
	print(i is MeshInstance3D)
	
	match i:
		"1":
			print(i)
		1:
			print(i)
		0 when true:
			print("zero!")
		#var x when false:
		#	print("unreachable")
		#[var x, var y] when true:
		#	print("array pattern")
		#{var x : var y} when true:
		#	print("dictionary pattern")
		_:
			print("unknown")
	
	i += 3/3 + 2*.5
	
	await jump
	await get_tree().process_frame
	
	get_tree().process_frame.emit(.7)
	get_tree().process_frame.connect(something)
	
	return []

var array = []
