using System;
using Godot;
using Dictionary = Godot.Collections.Dictionary;
using Array = Godot.Collections.Array;


public partial class script_level : Godot.Node
{
	public partial class Nested1 : test
	{
		
	}
	
	public partial class Nested2 : Godot.Object
	{
		
		public partial class Nested3 : Godot.Object
		{
			
		}
	}
	
	public enum Enum0 {UNIT_NEUTRAL,UNIT_ENEMY,UNIT_ALLY}
	public enum Named {THING_1,THING_2,ANOTHER_THING=-1}
	
	
	[Export]
	public Godot.Variant export;
	
	
	[Export("param1,param2")]
	public Godot.Variant export_param;
	
	
	[Export(PropertyHint.Flags,"Self:4,Allies:8,Foes:16")]
	public Godot.Variant export_flags;
	
	public double getset_var
	{
		set => _set(value);
		get => _get();
	}
	private double _getset_var;

	
	public double DEF =  - 0.1 // Step
	{
		set
		{
			set_sprite_offset(value);
		}
		get
		{
			return sprite_offset;
		}
	}
	private double _DEF;

	
	[Signal]
	public delegate void aHandler();
	[Signal]
	public delegate void bHandler(int a,Type b);
	
}