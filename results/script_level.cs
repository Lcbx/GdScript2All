using System;
using Godot;
using Dictionary = Godot.Collections.Dictionary;
using Array = Godot.Collections.Array;


public partial class script_level : Godot.Node
{
	public partial class Nested1 : test
	{

	}

	public partial class Nested4 : Godot.Object
	{

		public partial class Nested2 : Godot.Object
		{

		}

		public partial class Nested3 : Godot.Object
		{

		}
	}


	public enum Enum0 {UNIT_NEUTRAL,UNIT_ENEMY,UNIT_ALLY}
	public enum Named {THING_1,THING_2,ANOTHER_THING=-1}

	[Export]
	public Godot.Variant Export;

	[ExportGroup("with parameters")]

	[Export("param1,param2")]
	public Godot.Variant ExportParam;

	[ExportCategory("category")]

	[Export(PropertyHint.Flags"Self:4,Allies:8,Foes:16")]
	public Godot.Variant ExportFlags;

	[ExportGroup("group")]
	[ExportSubgroup("subgroup")]
	[Export] public double GetVar3
	{
		get
		{return _GetVar3;
		}
	}
	private double _GetVar3;


	public double GetsetVar
	{
		set => _Set(value);
		get => _Get();
	}
	private double _GetsetVar;


	public double DEF =  - 0.1 // comment
	{
		set
		{
			SetSpriteOffset(value);
		}
		get
		{
			return sprite_offset;
		}
	}
	private double _DEF;


	[Signal]
	public delegate void AHandler();
	[Signal]
	public delegate void BHandler(int c, Type d);

	protected override void _Ready()
	{
		GetsetVar = 0.0;
	}
}