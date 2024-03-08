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
	public partial class Nested1 : Godot.test
	{

	}

	public enum Enum0 {UNIT_NEUTRAL, UNIT_ENEMY, UNIT_ALLY}
	public enum NamedEnum {THING_1, THING_2, ANOTHER_THING =  - 1}

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
			GD.Print(K);
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
	public const ShaderMode enum = Godot.RenderingServer.ShaderMode.SHADER_SPATIAL;
	public double GlobalFunction = Mathf.AngleDifference(0.1, 0.2);

	// Gdscript special syntax
	public Godot.Node GetNode = GetNode("node");
	public Godot.Node GetNode2 = GetNode("../node");
	public Godot.Node GetUniqueNode = GetNode("%unique_node");
	public Godot.Resource PreloadResource = /* preload has no equivalent, add a 'ResourcePreloader' Node in your scene */("res://path");
	public Godot.Resource LoadResource = Load("res://path");

	// getters and setters
	public double Getset = 0.1
	{
		set => _Set(value);
		get => _Get();
	}
	private double _Getset;


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
	public delegate void JumpHandler();
	[Signal]
	public delegate void MovementHandler(Godot.Vector3 dir, double speed);

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

		EmitSignal("movement", Vector3.UP, 0.1);
	}

	// _ready generation when @onready is used
	public int K;


	protected override void _Ready()
	{
		K = 42;
	}
}