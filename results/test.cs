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
	public const string STR = "the fox said \"get off my lawn\"";
	public string BigStr = @"
		this is a multiline string
	";
	public Array Array = new Array{0, 1, 2, };
	public Dictionary Dict = new Dictionary{{0, 1},{1, 2},{2, 3},};
	public Array<string> StringArray = new Array{"0", "1", };
	
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
	public const int FLAG = Godot.RenderingServer.NO_INDEX_ARRAY;
	public double GlobalFunction = Mathf.AngleDifference(0.1, 0.2);
	
	// Gdscript special syntax
	public Godot.Node GetNode = GetNode("node");
	public Godot.Node GetNode2 = GetNode("../node");
	public Godot.Node GetUniqueNode = GetNode("%unique_node");
	public Godot.Resource PreloadResource = /* preload has no equivalent, add a 'ResourcePreloader' Node in your scene */("res://path");
	public Godot.Resource LoadResource = Load("res://path");
	
	// signals
	[Signal]
	public delegate void JumpHandler();
	[Signal]
	public delegate void MovementHandler(Godot.Vector3 dir, double speed);
	
	// property getters and setters
	public double GetsetVar
	{
		set => _Set(value);
		get => _Get();
	}
	private double _GetsetVar;

	
	public double GetsetVar2 =  - 0.1
	{
		set
		{
			_GetsetVar2 = value;
		}
		get
		{
			return _GetsetVar2;
		}
	}
	private double _GetsetVar2;

	
	public void AsyncFunction()
	{
		await ToSignal(this, "Jump");
		await ToSignal(GetTree(), "ProcessFrame");
		
		GetTree().EmitSignal("process_frame", 0.7);
		
		var myLambda = () =>
		{	GD.Print("look ma i'm jumping");
		};
		
		// lambdas are not perfectly translated
		jump += myLambda;
		
		EmitSignal("movement", Godot.Vector3.UP, 0.1);
	}
	
	// this becomes rapidly unreadable once translated though
	protected const Dictionary _DEFAULT_DATA = new Dictionary{
		{"t", 100},
		{"rafg", "asfgh"},
		{"u", false},// Example Comment
		{"r", new Array{"a", new Dictionary{{"b", false},}, }},
		{"t", new Dictionary{{"e", new Dictionary{{"g", 1},{"f", 2},}},}},
		};
	
	// automatic _ready generation
	public int K;
	
	protected override void _Ready()
	{
		K = 42;
	}
}