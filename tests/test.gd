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

@export_group('group')

@export_flags("Self:4", "Allies:8", "Foes:16")
var export_flags : int

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
var complex = {
	"t" : 100,
	"rafg" : 'asfgh',
	"u" : false, # Example Comment
	"t":{"e":{"g":1,"f":2},},
} ['rafg']

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
const enum = RenderingServer.SHADER_SPATIAL
var global_function = angle_difference(.1,.2)

# Gdscript special syntax
var get_node = $node
var get_node2 = $"../node"
var get_unique_node = %unique_node
var preload_resource = preload("res://path")
var load_resource = load("res://path")

# getters and setters
var getset_var := .1 : set = _set, get = _get

var getset_sprite : Sprite2D :
	set (value):
		getset_sprite = value
		getset_sprite.position = Vector2(1,2)
		getset_sprite.position += Vector2(1,2) # cpp will need help here
	get:
		return getset_sprite

func enumReturn(): return THING_2

# signals
signal jump
signal movement(dir:Vector3, speed:float)

func async_function():
	await jump
	await get_tree().process_frame
	
	get_tree().process_frame.emit(.7)
	
	var myLambda = func(): print("look ma i'm jumping")
	
	# lambdas are not perfectly translated
	jump.connect( myLambda )
	
	movement.emit(Vector3.UP, .1)

# _ready generation when @onready is used
@onready var k = 42

