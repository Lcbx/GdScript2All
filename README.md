## GdScript2All
A python tool for migrating GdScript to C# currently and eventually cpp with features like type inference (see example).

### Usage
```bash
py main.py -i <file_or_folder_path> -o <output_file_or_folder_path>
```

### Example
script input :
```GDScript
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
var x = self.get_parent()
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
```
C# output :
```cs
using System;
using Godot;
using Dictionary = Godot.Collections.Dictionary;
using Array = Godot.Collections.Array;



// line comment

/* multiline
   comment
*/

[Tool]
public partial class test : Godot.Node
{
	public partial class Nested1 : test
	{
		
	}
	
	enum Enum0 {UNIT_NEUTRAL,UNIT_ENEMY,UNIT_ALLY}
	enum Named {THING_1,THING_2,ANOTHER_THING=-1}
	
	
	[Export]
	public Godot.Variant export;
	
	
	[Export("param1,param2")]
	public Godot.Variant export_param;
	
	
	[Export(PropertyHint.Flags,"Self:4,Allies:8,Foes:16")]
	public Godot.Variant export_flags;
	
	// basic property definitions / expressions
	public Godot.Variant foo;
	public static int i = 0;
	public const string str = "the fox said \"get off my lawn\"";
	public string big_str = @"
		this is a multiline string
	";
	protected bool _protected_bool = true;
	public Array array = new Array{0,1,2,};
	public Dictionary dict = new Dictionary{{0,1},{1,2},{2,3},};
	public Array<string> string_array = new Array{"0","1",};
	public int parenthesis = (42);
	public int delayed_expression = 1;
	public double asKeyword = 3;
	
	
	// type inference
	public int j = this.i;
	public string k = string_array[0];
	
	// method
	public double method(double param = 5.0)
	{
		var val = 2;
		foreach(string k in string_array)
		{
			print(k);
		}
		return val * param;
	}
	
	// determine type based on godot doc
	public Godot.Node x = this.get_parent();
	public double x = new Vector3().x;
	public Godot.Vector3 up = Godot.Vector3.UP;
	public Dictionary aClass = Godot.ProjectSettings.get_global_class_list()[10];
	public const int flag = Godot.RenderingServer.NO_INDEX_ARRAY;
	public double global_function = angle_difference(0.1,0.2);
	
	// Gdscript special syntax
	public Godot.Node get_node = get_node("node");
	public Godot.Node get_unique_node = get_node("%unique_node");
	public Godot.Variant preload_resource = preload("res://path");
	public Godot.Variant load_resource = load("res://path");
	
	// get set
	public double getset_var;
	
	//PANIC! <: set = _set , get = _get> unexpected at Token(type=':', value=':', lineno=67, index=1303, end=1304)public double getset_var2 =  - 0.1;
	//PANIC! <:> unexpected at Token(type=':', value=':', lineno=69, index=1352, end=1353)
}
```
c++ output (TODO!) :
```c++
__test.hpp__
```
```c++
__test.cpp__
```

### Limitations
- read [TODO.md](TODO.md) for WIP features
- type inference does not currently support user-defined classes
- pattern matching ex:  
```
match [34, 6]:
  [0, var x]:
     print(x)
  [var y, 6] when y > 10 :
     print(y)
```
will probably not be supported (too complicated to generate an equivalent)

### To update the API definition
* clone the offical godot repo
* copy it's ```doc/classes``` folder and paste it into our ```classData``` folder
* install untangle (xml parsing library) if you don't have it (```pip install untangle```)
* run ```py src/godot_types.py``` to generate the pickle class db
* profit.

### Explaining the GPL-3.0 license
The code this tool generates from your GDScipt is yours.
However, any modifications made to this tool's source has to be available to the open-source community.
I think that is a fair deal.
  
<a href="https://www.buymeacoffee.com/Lcbx" target="_blank"><img src="https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png" alt="Buy Me A Coffee" style="box-shadow: 0px 3px 2px 0px rgba(190, 190, 190, 0.5) !important;-webkit-box-shadow: 0px 3px 2px 0px rgba(190, 190, 190, 0.5) !important;" ></a>

