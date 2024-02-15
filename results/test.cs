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