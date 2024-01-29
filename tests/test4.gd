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
const string = 'the fox said "get off my lawn"'
var int = 0
var _bool := true

@export
var array : Array[int] = [0,1,2]

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

var get_node = $node
var get_unique_node = %unique_node
var preload_resource = preload("res://path")
var load_resource = load("res://path")

var getset_var:float : set = _set_state, get = _get_state

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

func setterA(v:float):
	return
	pass

func getterA()->float:
	return 1.

func ready():
	var s = range(abs(-1),randi())
	
	.ready();

    if ABC: # Comment
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