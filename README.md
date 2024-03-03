## GdScript2All
A python tool for migrating [Godot](https://github.com/godotengine/godot)'s GdScript to other languages (currently C# and c++) with features like type inference.
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
const flag = RenderingServer.NO_INDEX_ARRAY
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
    [Tool]
    public partial class Nested1 : test
    {

    }

    public enum Enum0 {UNIT_NEUTRAL,UNIT_ENEMY,UNIT_ALLY}
    public enum Named {THING_1,THING_2,ANOTHER_THING=-1}

    [Export]
    public Godot.Variant Export;

    [Export("param1,param2")]
    public Godot.Variant ExportParam;

    [ExportGroup("group")]

    [Export(PropertyHint.Flags"Self:4,Allies:8,Foes:16")]
    public int ExportFlags;

    // basic property definitions / expressions
    public Godot.Variant Foo;
    public static int I = 0;
    public const string str = "the fox said \"get off my lawn\"";
    public string BigStr = @"
            this is a multiline string
        ";
    public Array Array = new Array{0, 1, 2, };
    public Dictionary Dict = new Dictionary{{0, 1},{1, 2},{2, 3},};
    public Array<string> StringArray = new Array{"0", "1", };
    public Godot.Variant Complex = new Dictionary{
                {"t", 100},
                {"rafg", "asfgh"},
                {"u", false},// Example Comment
                {"t", new Dictionary{{"e", new Dictionary{{"g", 1},{"f", 2},}},}},
                }["rafg"];

    // method
    public double Method(double param = 5.0)
    {
        var val = 2;
        foreach(string k in StringArray)
        {
            GD.Print(k);
        }
        return val * param;
    }

    // type inference on members
    public int J = this.I;
    public string K = StringArray[0];

    // determine type based on godot doc
    public Godot.Node X = this.GetParent();
    public double X = new Vector3().X;
    public Dictionary AClass = Godot.ProjectSettings.GetGlobalClassList()[10];
    public const int flag = Godot.RenderingServer.NO_INDEX_ARRAY;
    public double GlobalFunction = Mathf.AngleDifference(0.1, 0.2);

    // Gdscript special syntax
    public Godot.Node GetNode = GetNode("node");
    public Godot.Node GetNode2 = GetNode("../node");
    public Godot.Node GetUniqueNode = GetNode("%unique_node");
    public Godot.Resource PreloadResource = /* preload has no equivalent, add a 'ResourcePreloader' Node in your scene */("res://path");
    public Godot.Resource LoadResource = Load("res://path");

    // getters and setters
    public double GetsetVar = 0.1
    {
        set => _Set(value);
        get => _Get();
    }
    private double _GetsetVar;


    public Godot.Sprite2D GetsetSprite
    {
        set
        {
            _GetsetSprite = value;
            _GetsetSprite.Position = new Vector2(1, 2);
            _GetsetSprite.Position += new Vector2(1, 2);// cpp will need help here
        }
        get
        {
            return _GetsetSprite;
        }
    }
    private Godot.Sprite2D _GetsetSprite;


    // signals
    [Signal]
    public delegate void JumpHandler();
    [Signal]
    public delegate void MovementHandler(Godot.Vector3 dir, double speed);

    public void AsyncFunction()
    {
        await ToSignal(this, "Jump");
        await ToSignal(GetTree(), "ProcessFrame");

        GetTree().EmitSignal("process_frame", 0.7);

        var myLambda = () =>
        {    GD.Print("look ma i'm jumping");
        };

        // lambdas are not perfectly translated
        jump += myLambda;

        EmitSignal("movement", Godot.Vector3.UP, 0.1);
    }

    // _ready generation when @onready is used
    public int K;


    protected override void _Ready()
    {
        K = 42;
    }
}
```
c++ output (header) :
```c++

#ifndef TEST_H
#define TEST_H

#include <godot_cpp/godot.hpp>

using namespace godot;

namespace godot {

// line comment

/* multiline
   comment
*/

class Nested1 : public test {
    GDCLASS(Nested1, test);
public:

}

class test : public Node {
    GDCLASS(test, Node);
public:
    enum  {UNIT_NEUTRAL,UNIT_ENEMY,UNIT_ALLY};
    enum Named {THING_1,THING_2,ANOTHER_THING=-1};

protected:
    Variant export;

    Variant export_param;

    int export_flags;

// basic property definitions / expressions
    Variant foo;
    static int i = 0;
    const string str = "the fox said \"get off my lawn\"";
    string big_str = "\
    this is a multiline string\
";
    Array array = new Array{0, 1, 2, };
    Dictionary dict = new Dictionary{{0, 1},{1, 2},{2, 3},};
    Array<string> string_array = new Array{"0", "1", };
    Variant complex = new Dictionary{
        {"t", 100},
        {"rafg", "asfgh"},
        {"u", false},// Example Comment
        {"t", new Dictionary{{"e", new Dictionary{{"g", 1},{"f", 2},}},}},
        }["rafg"];

// method

// type inference on members

public:
    float method(float param = 5.0);

protected:
    int j = this->i;
    string k = string_array[0];

// determine type based on godot doc
    Node* x = this->get_parent();
    float x = Vector3().x;
    Dictionary aClass = ProjectSettings::get_singleton()->get_global_class_list()[10];
    const int flag = RenderingServer::NO_INDEX_ARRAY;
    float global_function = angle_difference(0.1, 0.2);

// Gdscript special syntax
    Node* get_node = get_node("node");
    Node* get_node2 = get_node("../node");
    Node* get_unique_node = get_node("%unique_node");
    Resource* preload_resource = /* preload has no equivalent, add a 'ResourcePreloader' Node in your scene */("res://path");
    Resource* load_resource = load("res://path");

// getters and setters
    float getset_var = 0.1;

    Sprite2D* getset_sprite;

public:
    void set_getset_sprite(Sprite2D* value);

// signals
    Sprite2D* get_getset_sprite();
    /* signal jump() */
    /* signal movement(Vector3 dir, float speed) */

// _ready generation when @onready is used
    void async_function();

protected:
    int k;

public:
    void _ready() override;
    void set_export(Variant value);
    Variant get_export();
    void set_export_param(Variant value);
    Variant get_export_param();
    void set_export_flags(int value);
    int get_export_flags();

    static void _bind_methods();
}

}

#endif // TEST_H

```
c++ output (implementation) :
```c++

#include "test.hpp"
#include <godot_cpp/core/object.hpp>
#include <godot_cpp/core/class_db.hpp>

float test::method(float param)
{
    int val = 2;
    for(string k : string_array)
    {
        print(k);
    }
    return val * param;
}

void test::set_getset_sprite(Sprite2D* value)
{
    getset_sprite = value;
    getset_sprite->set_position(Vector2(1, 2));
    getset_sprite->set_position( /* position += */ + Vector2(1, 2));// cpp will need help here
}

Sprite2D* test::get_getset_sprite()
{
    return getset_sprite;
}

void test::async_function()
{
    /* await this->jump; */ // no equivalent to await in c++ !
    /* await this->get_tree()->process_frame; */ // no equivalent to await in c++ !

    get_tree()->emit_signal("process_frame", 0.7);

    Callable myLambda = []() 
    {    print("look ma i'm jumping");
    };

    // lambdas are not perfectly translated
    connect("jump", myLambda);

    emit_signal("movement", Vector3::UP, 0.1);
}

void test::_ready()
{
    k = 42;
}

void test::set_export(Variant value) {
    export = value;
}

Variant test::get_export() {
    return export;
}

void test::set_export_param(Variant value) {
    export_param = value;
}

Variant test::get_export_param() {
    return export_param;
}

void test::set_export_flags(int value) {
    export_flags = value;
}

int test::get_export_flags() {
    return export_flags;
}

static void test::_bind_methods() {
    ClassDB::bind_method(D_METHOD("method", "param"), &test::method);
    ClassDB::bind_method(D_METHOD("set_getset_sprite", "value"), &test::set_getset_sprite);
    ClassDB::bind_method(D_METHOD("get_getset_sprite"), &test::get_getset_sprite);
    ClassDB::bind_method(D_METHOD("async_function"), &test::async_function);
    ClassDB::bind_method(D_METHOD("set_export", "value"), &test::set_export);
    ClassDB::bind_method(D_METHOD("get_export"), &test::get_export);
    ClassDB::bind_method(D_METHOD("set_export_param", "value"), &test::set_export_param);
    ClassDB::bind_method(D_METHOD("get_export_param"), &test::get_export_param);
    ClassDB::bind_method(D_METHOD("set_export_flags", "value"), &test::set_export_flags);
    ClassDB::bind_method(D_METHOD("get_export_flags"), &test::get_export_flags);

    ADD_PROPERTY(PropertyInfo(Variant::OBJECT, "export"), "set_export", "get_export");
    ADD_PROPERTY(PropertyInfo(Variant::OBJECT, "export_param"), "set_export_param", "get_export_param");
    ADD_GROUP("group","");
    ADD_PROPERTY(PropertyInfo(Variant::INT, "export_flags", PROPERTY_HINT_FLAGS, "Self:4,Allies:8,Foes:16"), "set_export_flags", "get_export_flags");
    ADD_SIGNAL(MethodInfo("jump"));
    ADD_SIGNAL(MethodInfo("movement", PropertyInfo(Variant::VECTOR3, "dir"), PropertyInfo(Variant::FLOAT, "speed")));
}


```

### Adding new languages
If you want to transpile to an unsupported language, rename a copy of the [C# transpiler backend](src/CsharpTranspiler.py),
modify it as needed, then to use it you just have to pass its name with the ```-t``` flag (example below with c++ transpiler):
```bash
py main.py -t Cpp <file_or_folder_path>
```

### Limitations
- read [TODO.md](TODO.md) for WIP features
- type inference does not currently support user-defined classes
- generated C++ does not add necessary includes nor does it handle pointers well
- pattern matching ex:  
```GDScript
match [34, 6]:
  [0, var y]:
     print(y)
  [var x, 6] when x > 10 :
     print(x)
```
will probably not be supported (too complicated to generate an equivalent)

### Updating the API definition
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

