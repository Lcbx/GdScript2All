## GdScript2All
A python tool for migrating [Godot](https://github.com/godotengine/godot)'s GdScript to any languages (C# only currently but eventually c++) with features like type inference.
It should be fairly easy to add new langugages (see [here](#Adding-new-languages))

### Usage
```bash
py main.py <file_or_folder_path> -o <output_file_or_folder_path>
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

# this becomes rapidly unreadable once translated though
const _default_data = {
	"t" : 100,
	"rafg" : 'asfgh',
	"u" : false,# Example Comment
	"r":["a",{"b":false}],
	"t":{"e":{"g":1,"f":2},},
}


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
	
	public enum Enum0 {UNIT_NEUTRAL,UNIT_ENEMY,UNIT_ALLY}
	public enum Named {THING_1,THING_2,ANOTHER_THING=-1}
	
	
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
	public Array array = new Array{0,1,2,};
	public Dictionary dict = new Dictionary{{0,1},{1,2},{2,3},};
	public Array<string> string_array = new Array{"0","1",};
	
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
	
	// type inference on members
	public int j = this.i;
	public string k = string_array[0];
	
	// determine type based on godot doc
	public Godot.Node x = this.get_parent();
	public double x = new Vector3().x;
	public Dictionary aClass = Godot.ProjectSettings.get_global_class_list()[10];
	public const int flag = Godot.RenderingServer.NO_INDEX_ARRAY;
	public double global_function = angle_difference(0.1,0.2);
	
	// Gdscript special syntax
	public Godot.Node get_node = get_node("node");
	public Godot.Node get_unique_node = get_node("%unique_node");
	public Godot.Variant preload_resource = preload("res://path");
	public Godot.Variant load_resource = load("res://path");
	
	// signals
	[Signal]
	public delegate void jumpHandler();
	[Signal]
	public delegate void movementHandler(Godot.Vector3 dir,double speed);
	
	// property getters and setters
	public double getset_var
	{
		set => _set(value);
		get => _get();
	}
	private double _getset_var;

	
	public double getset_var2 =  - 0.1
	{
		set
		{
			_getset_var2 = value;
		}
		get
		{
			return _getset_var2;
		}
	}
	private double _getset_var2;

	
	public void async_function()
	{
		await;jump;
	}
	
	// this becomes rapidly unreadable once translated though
	protected const Dictionary _default_data = new Dictionary{
	{"t",100},
	{"rafg","asfgh"},
	{"u",false},// Example Comment
	{"r",new Array{"a",new Dictionary{{"b",false},},}},
	{"t",new Dictionary{{"e",new Dictionary{{"g",1},{"f",2},}},}},
	};
	
	
}
```
c++ output (TODO!) :
```c++
__test.hpp__
```
```c++
__test.cpp__
```

### Adding new languages
If you want to transpile to an unsupported language, rename a copy of the [C# transpiler backend](src/CsharpTranspiler.py),
modify it as needed, then to use it you just have to pass its name with the ```-t``` flag:
```bash
py main.py -t CustomTranspiler <file_or_folder_path>
```

### Limitations
- read [TODO.md](TODO.md) for WIP features
- type inference does not currently support user-defined classes
- pattern matching ex:  
```GDScript
match [34, 6]:
  [0, var y]:
     print(y)
  [var x, 6] when x > 10 :
     print(x)
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

