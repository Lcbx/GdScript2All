using System;
using Godot;
using Dictionary = Godot.Collections.Dictionary;
using Array = Godot.Collections.Array;



[Tool]
public partial class test : Godot.Node
{
	// line comment
	
	/* multiline
	   comment
	*/
	
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
		return val * param;
	}
	
	// determine type based on godot doc
	public double x = new Vector3().x;
	public Godot.Vector3 up = Godot.Vector3.UP;
	public Dictionary aClass = Godot.ProjectSettings.get_global_class_list()[10];
	public const int flag = Godot.RenderingServer.NO_INDEX_ARRAY;
	
	// Gdscript special syntax
	public Godot.Node get_node = get_node("node");
	public Godot.Node get_unique_node = get_node("%unique_node");
	public Godot.Variant preload_resource = preload("res://path");
	public Godot.Variant load_resource = load("res://path");
	
	// get set
	public double getset_var;
	
	//PANIC! <: set = _set , get = _get> unexpected at Token(type=':', value=':', lineno=63, index=1196, end=1197)public double getset_var2 =  - 0.1;
	//PANIC! <:> unexpected at Token(type=':', value=':', lineno=65, index=1245, end=1246)
}