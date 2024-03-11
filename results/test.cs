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
		{	GD.Print("look ma i'm jumping");
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