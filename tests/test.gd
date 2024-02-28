@tool
extends Node

# line comment

""" multiline
   comment
"""

class Nested1 extends test:

enum {UNIT_NEUTRAL, UNIT_ENEMY, UNIT_ALLY}
enum Named {THING_1, THING_2, ANOTHER_THING = -1}

@export
var export

@export(param1, param2)
var export_param

@export_flags("Self:4", "Allies:8", "Foes:16")
var export_flags

# basic property definitions / expressions
var foo
static var i = 0
const str = 'the fox said "get off my lawn"'
var big_str : string = """
	this is a multiline string
"""
var array = [0,1,2]
var dict := {0:1, 1:2, 2:3}
var string_array : Array[string] = ['0','1']

# method
func method(param = 5.):
	var val = 2
	for k in string_array:
		print(k)
	return val * param

# type inference on members
var j = self.i
var k = string_array[0]

# determine type based on godot doc
var x = self.get_parent()
var x = Vector3().x
var aClass = ProjectSettings.get_global_class_list()[10]
const flag = RenderingServer.NO_INDEX_ARRAY
var global_function = angle_difference(.1,.2)

# Gdscript special syntax
var get_node = $node
var get_node2 = $"../node"
var get_unique_node = %unique_node
var preload_resource = preload("res://path")
var load_resource = load("res://path")

# signals
signal jump
signal movement(dir:Vector3, speed:float)

# property getters and setters
var getset_var : float : set = _set, get = _get

var getset_var2 = -0.1 :
	set (value):
		getset_var2 = value
	get:
		return getset_var2

func async_function():
	await jump
	await get_tree().process_frame
	
	get_tree().process_frame.emit(.7)
	
	var myLambda = func(): print("look ma i'm jumping")
	
	# lambdas are not perfectly translated
	jump.connect( myLambda )
	
	movement.emit(Vector3.UP, .1)

# this becomes rapidly unreadable once translated though
const _default_data = {
	"t" : 100,
	"rafg" : 'asfgh',
	"u" : false,# Example Comment
	"r":["a",{"b":false}],
	"t":{"e":{"g":1,"f":2},},
}

# automatic _ready generation
@onready var k = 42

