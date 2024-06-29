## GdScript2All
A tool for converting [Godot](https://github.com/godotengine/godot)'s GdScript to other languages (currently C# and c++) with features like type inference, written in Python.
It should be fairly easy to add new languages (see [here](#Adding-new-languages)).

#### Editor addon (windows only)
Download as a zip (not yet available from the Godot asset library), extract into your project and enable the plugin in your project settings.

#### From the command line
with python 3.9+ installed, call the main script using your favorite command line utility (add ```-t Cpp``` for c++) :
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
const str = 'the fox said "get off my lawn"'
var big_str : string = """
    this is a multiline string """
var array = [0,1,2]
var dict := {0:1, 1:2, 2:3}
var string_array : Array[string] = ['0','1']

func method(param = 5.):
    for k in string_array:
        print(k)
    return val * param

# type inference on members
var j = i
var k = string_array[0]

# determine type based on godot doc
var x = self.get_parent()
var aClass = ProjectSettings.get_global_class_list()[10]
const enum = RenderingServer.SHADER_SPATIAL
var function = angle_difference(.1,.2)

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

func enum_return(): return THING_2

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
using Godot.Collections;



// line comment

/* multiline
   comment
*/

[Tool]
[GlobalClass]
public partial class test : Godot.Node
{
    [Tool]
    public partial class Nested1 : Godot.test
    {

    }

    public enum Enum0 {UNIT_NEUTRAL, UNIT_ENEMY, UNIT_ALLY}
    public enum NamedEnum {THING_1, THING_2, ANOTHER_THING =  - 1}

    [Export]
    public Godot.Variant Export;

    [ExportGroup("group")]

    [Export(PropertyHint.Flags, "Self:4,Allies:8,Foes:16")]
    public int ExportFlags;

    // basic property definitions / expressions
    public static int I = 0;
    public const string str = "the fox said \"get off my lawn\"";
    public string BigStr = @"
    this is a multiline string ";
    public Array Array = new Array{0, 1, 2, };
    public Dictionary Dict = new Dictionary{{0, 1},{1, 2},{2, 3},};
    public Array<string> StringArray = new Array{"0", "1", };

    public double Method(double param = 5.0)
    {
        foreach(string k in StringArray)
        {
            GD.Print(K);
        }
        return val * param;
    }

    // type inference on members
    public int J = I;
    public string K = StringArray[0];

    // determine type based on godot doc
    public Godot.Node X = this.GetParent();
    public Dictionary AClass = Godot.ProjectSettings.GetGlobalClassList()[10];
    public const RenderingServer.ShaderMode enum = Godot.RenderingServer.ShaderMode.ShaderSpatial;
    public double Function = Mathf.AngleDifference(0.1, 0.2);

    // Gdscript special syntax
    public Godot.Node GetNode = GetNode("node");
    public Godot.Node GetNode2 = GetNode("../node");
    public Godot.Node GetUniqueNode = GetNode("%unique_node");
    public Godot.Resource PreloadResource = /* preload has no equivalent, add a 'ResourcePreloader' Node in your scene */("res://path");
    public Godot.Resource LoadResource = Load("res://path");

    public Godot.Sprite2D Sprite
    {
        set
        {
            _Sprite = value;
            _Sprite.Position = new Vector2(1, 2);
            _Sprite.Position += new Vector2(1, 2);// cpp will need help here
        }
        get
        {
            return _Sprite;
        }
    }
    private Godot.Sprite2D _Sprite;


    public NamedEnum EnumReturn()
    {return THING_2;
    }

    // signals
    [Signal]
    public delegate void JumpEventHandler();
    [Signal]
    public delegate void MovementEventHandler(Vector3 dir, double speed);

    public void AsyncFunction()
    {
        await ToSignal(this, "Jump");
        await ToSignal(GetTree(), "ProcessFrame");

        GetTree().EmitSignal("ProcessFrame", 0.7);

        var myLambda = () =>
        {    GD.Print("look ma i'm jumping");
        };

        // lambdas are not perfectly translated
        Jump += myLambda;

        EmitSignal("Movement", Vector3.Up, 0.1);
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
#include <godot_cpp/variant/array.hpp>
#include <godot_cpp/variant/dictionary.hpp>
#include <godot_cpp/classes/node.hpp>
#include <godot_cpp/classes/resource.hpp>
#include <godot_cpp/classes/sprite2d.hpp>
#include <godot_cpp/classes/test.hpp>

using namespace godot;

// line comment

/* multiline
   comment
*/

class Nested1 : public test {
    GDCLASS(Nested1, test);
public:

};

class test : public Node {
    GDCLASS(test, Node);
public:
    enum  {UNIT_NEUTRAL, UNIT_ENEMY, UNIT_ALLY};
    enum NamedEnum {THING_1, THING_2, ANOTHER_THING =  - 1};

protected:
    Variant export;

    int export_flags;

// basic property definitions / expressions
    static int i;
    const String str = "the fox said \"get off my lawn\"";
    String big_str = "\
    this is a multiline string ";
    Array array =  /* no array initializer in c++ ! */ {0, 1, 2, };
    Dictionary dict =  /* no dictionary initializer in c++ ! */ {{0, 1},{1, 2},{2, 3},};
    Array string_array =  /* no array initializer in c++ ! */ {"0", "1", };

// type inference on members

public:
    double method(double param = 5.0);

protected:
    int j = i;
    String k = string_array[0];

// determine type based on godot doc
    Ref<Node> x = this->get_parent();
    Dictionary aClass = ProjectSettings::get_singleton()->get_global_class_list()[10];
    const RenderingServer::ShaderMode enum = RenderingServer::ShaderMode::SHADER_SPATIAL;
    double function = Math::angle_difference(0.1, 0.2);

// Gdscript special syntax
    Ref<Node> get_node = get_node("node");
    Ref<Node> get_node2 = get_node("../node");
    Ref<Node> get_unique_node = get_node("%unique_node");
    Ref<Resource> preload_resource = /* preload has no equivalent, add a 'ResourcePreloader' Node in your scene */("res://path");
    Ref<Resource> load_resource = load("res://path");

    Ref<Sprite2D> sprite;

public:
    void set_sprite(Ref<Sprite2D> value);

    Ref<Sprite2D> get_sprite();

// signals
    NamedEnum enum_return();
    /* signal jump() */
    /* signal movement(Vector3 dir, double speed) */

// _ready generation when @onready is used
    void async_function();

protected:
    int k;

public:
    void _ready() override;
    void set_export(Variant value);
    Variant get_export();
    void set_export_flags(int value);
    int get_export_flags();

    static void _bind_methods();
};

VARIANT_ENUM_CAST(test::NamedEnum)

#endif // TEST_H

```
c++ output (implementation) :
```c++

#include "test.hpp"

#include <godot_cpp/core/object.hpp>
#include <godot_cpp/core/class_db.hpp>
#include <godot_cpp/variant/utility_functions.hpp>

double test::method(double param)
{
    for(String k : string_array)
    {
        UtilityFunctions::print(k);
    }
    return val * param;
}

void test::set_sprite(Ref<Sprite2D> value)
{
    sprite = value;
    sprite->set_position(Vector2(1, 2));
    sprite->set_position( /* get_position() */ + Vector2(1, 2));// cpp will need help here
}

Ref<Sprite2D> test::get_sprite()
{
    return sprite;
}

NamedEnum test::enum_return()
{return THING_2;
}

void test::async_function()
{
    /* await this->jump; */ // no equivalent to await in c++ !
    /* await this->get_tree()->process_frame; */ // no equivalent to await in c++ !

    get_tree()->emit_signal("process_frame", 0.7);

    Callable myLambda = []() 
    {    UtilityFunctions::print("look ma i'm jumping");
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

void test::set_export_flags(int value) {
    export_flags = value;
}

int test::get_export_flags() {
    return export_flags;
}

void test::_bind_methods() {
    ClassDB::bind_method(D_METHOD("method", "param"), &test::method);
    ClassDB::bind_method(D_METHOD("enum_return"), &test::enum_return);
    ClassDB::bind_method(D_METHOD("async_function"), &test::async_function);
    ClassDB::bind_method(D_METHOD("set_sprite", "value"), &test::set_sprite);
    ClassDB::bind_method(D_METHOD("get_sprite"), &test::get_sprite);
    ClassDB::bind_method(D_METHOD("set_export", "value"), &test::set_export);
    ClassDB::bind_method(D_METHOD("get_export"), &test::get_export);
    ClassDB::bind_method(D_METHOD("set_export_flags", "value"), &test::set_export_flags);
    ClassDB::bind_method(D_METHOD("get_export_flags"), &test::get_export_flags);
    ClassDB::bind_integer_constant(get_class_static(), _gde_constant_get_enum_name(UNIT_NEUTRAL, "UNIT_NEUTRAL"), "UNIT_NEUTRAL", UNIT_NEUTRAL);
    ClassDB::bind_integer_constant(get_class_static(), _gde_constant_get_enum_name(UNIT_ENEMY, "UNIT_ENEMY"), "UNIT_ENEMY", UNIT_ENEMY);
    ClassDB::bind_integer_constant(get_class_static(), _gde_constant_get_enum_name(UNIT_ALLY, "UNIT_ALLY"), "UNIT_ALLY", UNIT_ALLY);
    ClassDB::bind_integer_constant(get_class_static(), _gde_constant_get_enum_name(THING_1, "THING_1"), "THING_1", THING_1);
    ClassDB::bind_integer_constant(get_class_static(), _gde_constant_get_enum_name(THING_2, "THING_2"), "THING_2", THING_2);
    ClassDB::bind_integer_constant(get_class_static(), _gde_constant_get_enum_name(ANOTHER_THING, "ANOTHER_THING"), "ANOTHER_THING", ANOTHER_THING);
    ClassDB::add_property(get_class_static(), PropertyInfo(Variant::OBJECT, "export"), "set_export", "get_export");
    ClassDB::add_property_group(get_class_static(), "group","");
    ClassDB::add_property(get_class_static(), PropertyInfo(Variant::INT, "export_flags", PROPERTY_HINT_FLAGS, "Self:4,Allies:8,Foes:16"), "set_export_flags", "get_export_flags");
    ClassDB::add_signal(get_class_static(), MethodInfo("jump"));
    ClassDB::add_signal(get_class_static(), MethodInfo("movement", PropertyInfo(Variant::VECTOR3, "dir"), PropertyInfo(Variant::FLOAT, "speed")));
}


```

### Adding new languages
If you want to transpile to an unsupported language, rename a copy of the [C# transpiler backend](src/CsharpTranspiler.py),
modify it as needed, then to use it you just have to pass its name with the ```-t``` flag (example below with c++ transpiler):
```bash
py main.py -t Cpp <file_or_folder_path>
```

### Limitations
- generated code might need corrections ! (indentation might need a second pass too)
- this tool parses and emits code ; if it encounters something unexpected it will drop the current line and try to resume at the next (panic mode)
- generated C++ does a best guess on what should be a pointer/reference
- in c++ accessing/modifying parent class properties does not use getters/setters (this is a conscious choice)
- read [TODO.md](TODO.md) for current/missing features
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
However, any improvment made to this tool's source has to be contributed back.
I think that's fair.
  
<a href="https://www.buymeacoffee.com/Lcbx" target="_blank"><img src="https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png" alt="Buy Me A Coffee" style="box-shadow: 0px 3px 2px 0px rgba(190, 190, 190, 0.5) !important;-webkit-box-shadow: 0px 3px 2px 0px rgba(190, 190, 190, 0.5) !important;" ></a>

