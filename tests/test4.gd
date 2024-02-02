@tool
extends Node

# line comment

""" multiline
   comment
"""

class Nested1 extends test:
			
class Nested2:
	class Nested3:
	

enum {UNIT_NEUTRAL, UNIT_ENEMY, UNIT_ALLY}
enum Named {THING_1, THING_2, ANOTHER_THING = -1}

var foo
var i = 0
const str = 'the fox said "get off my lawn"'
var big_str : string = """
this is a multiline string
"""
var _protected_bool := true
var array = [0,1,2]

@export
var string_array : Array[string] = ['0','1']

@export(param1, param2)
var dict := {0:1, 1:2, 2:3}

@export_flags("Self:4", "Allies:8", "Foes:16")
var parenthesis := (42)

var variable = foo
var reference = foo.bar
var function = foo()
var functionParams = foo(a,b)
var method = foo.bar()
var functionMethodParams = foo(a,b).bar(c,d)
var refMethod = foo.bar.baz()
var methodRef = foo.bar().baz
var subscription = self.dict[0]

# test type inference on local class members
var j = self.i
var k = string_array[0]

# determine type based on godot doc
var x = Vector3().x 
static var gravity = ProjectSettings.get_setting("physics/3d/default_gravity")
var aClass = ProjectSettings.get_global_class_list()[10]
const flag = RenderingServer.NO_INDEX_ARRAY

# Gdscript special syntax
var get_node = $node
var get_unique_node = %unique_node
var preload_resource = preload("res://path")
var load_resource = load("res://path")

var delayed = \
	1
var delayed_wComment = \ # comment
	2

var arithmetic = - j * .5
var comparison = arithmetic >= .5 and arithmetic == 6.
var ternary = not true if false && true else 5 > 6
var nested_ternary = true if false else 5 > 6 if true else 7 < 0

# methods
func empty(v:float):
	pass

func returning()->float:
	empty(7.)
	return 1.

var getset_var:float : set = _set, get = _get

var DEF = -0.1 # Step
	set (value):
		set_sprite_offset(value)
	get:
		return sprite_offset

var f = typeof(4+6/12)

signal a()
signal b(a:int,b:Type)

var string_test_1 = 'an "Elephant"'
var string_test_2 = 'an
 \'Elephantos\''

# "Default" 'Data' (I recommend splitting this kind of stuff into separate json files in c#)
const _default_data = {
	"t" : 100,
	"r
	afg" : 'asfgh',
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