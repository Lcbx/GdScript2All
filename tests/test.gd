@tool
extends Node

# line comment

""" multiline
   comment
"""

class Nested1 extends test: pass

enum {UNIT_NEUTRAL, UNIT_ENEMY, UNIT_ALLY}
enum NamedEnum {THING_1, THING_2, ANOTHER_THING = -1}

@export
var export

@export_group('group')

@export_flags("Self:4", "Allies:8", "Foes:16")
var export_flags : int

# basic property definitions / expressions
static var i = 0
const STRING_CONSTANT = 'the fox said "get off my lawn"'
var big_str : string = """
	this is a multiline string """
var array = [0,1,2]
var has_call = 3 in array
var dict := {0:1, 1:2, 2:3}
var string_array : Array[string] = ['0','1']

# type inference
var j = i
func method(param = 5.):
	for k in string_array:
		print(k)
	return val * param

# determine type based on godot doc
var x = self.get_parent()
var aClass = ProjectSettings.get_global_class_list()[10]
const enum = RenderingServer.SHADER_SPATIAL

# Gdscript special syntax
var get_node = $node
var get_node2 = $"../node"
var get_unique_node = %unique_node
var preload_resource = preload("res://path")
var load_resource = load("res://path")

var sprite : Sprite2D :
	set (value):
		sprite = value
		sprite.position = Vector2(1,2)
		sprite.position += Vector2(1,2) # cpp will need help here
	get:
		return sprite

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

