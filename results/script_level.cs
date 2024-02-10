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
	
	enum Enum0 {UNIT_NEUTRAL,UNIT_ENEMY,UNIT_ALLY}
	enum Named {THING_1,THING_2,ANOTHER_THING=-1}
	
	[Export]
	public Godot.Variant export;
	
	[Export("param1,param2")]
	public Godot.Variant export_param;
	
	[Export(PropertyHint.Flags,"Self:4,Allies:8,Foes:16")]
	public Godot.Variant export_flags;
	
	public double getset_var;
	
	//PANIC! <: set = _set , get = _get> unexpected at Token(type=':', value=':', lineno=20, index=322, end=323)public double DEF =  - 0.1;
	//PANIC! <:  Step> unexpected at Token(type=':', value=':', lineno=22, index=362, end=363)
}