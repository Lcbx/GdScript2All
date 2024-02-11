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
var _protected_bool := true
var array = [0,1,2]
var dict := {0:1, 1:2, 2:3}
var string_array : Array[string] = ['0','1']
var parenthesis := (42)
var delayed_expression = \
	1
var asKeyword = 3 as float


# type inference
var j = self.i
var k = string_array[0]

# method
func method(param = 5.):
	var val = 2
	for k in string_array:
		print(k)
	return val * param

# determine type based on godot doc
var x = Vector3().x 
var up = Vector3.UP
var aClass = ProjectSettings.get_global_class_list()[10]
const flag = RenderingServer.NO_INDEX_ARRAY
var global_function = angle_difference(.1,.2)

# Gdscript special syntax
var get_node = $node
var get_unique_node = %unique_node
var preload_resource = preload("res://path")
var load_resource = load("res://path")

# get set
var getset_var : float : set = _set, get = _get

var getset_var2 = -0.1 :
	set (value):
		set_sprite_offset(value)
	get:
		return sprite_offset

# signals
signal a()
signal b(a:int,b:Type)

# global functions
var f = typeof(4+6/12)

# "Default" 'Data' (I recommend splitting this kind of stuff into separate json files in c#)
const _default_data = {
	"t" : 100,
	"rafg" : 'asfgh',
	"u" : false,# Example Comment
	"r":["a",{"b":false}],
	"t":{"e":{"g":1,"f":2},},
};


func ready():
	var s = range(abs(-1),randi())
	
	ready();

	if ABC:
		assert(false)
	elif false:
		print("Hello"+" "+"World")
	else:
		(a+b)()
	return [
		[0,e,[0,{}]], # a
		[1,{},[0,{}]],
	];

# Do stuff
func r(value:T,val=false,s)->bool:
	if value == null : return !true

	var type = typeof(value)
	match type :
		TYPE_BOOL,TYPE_INT,TYPE_NIL:
			return value
		TYPE_DICTIONARY:
			var result = {}
			for k in value:
				result[k] = value[k]
			return result

func default_async_function():
	yield(self,'a');