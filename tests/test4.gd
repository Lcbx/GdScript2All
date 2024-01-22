@tool
extends Node


enum {UNIT_NEUTRAL, UNIT_ENEMY, UNIT_ALLY}
enum Named {THING_1, THING_2, ANOTHER_THING = -1}

@export(Date,Param)      const Date = preload("res://path")
const ABC = true
var G:float setget setterA, getterA
var DEF = -0.1 # Step

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