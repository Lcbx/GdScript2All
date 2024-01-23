using System;
using Godot;
using Dictionary = Godot.Collections.Dictionary;
using Array = Godot.Collections.Array;



[Tool]
public partial class test4 : Godot.Node
{
	public partial class Nested1 : test
	{
		
		
	}
	public partial class Nested2 : Godot.Object
	{
		
		
		
	}
	enum Enum0 {UNIT_NEUTRAL, UNIT_ENEMY, UNIT_ALLY}
	enum Named {THING_1, THING_2, ANOTHER_THING = -1}
	
	public const <class 'int'> i = 0;
	
	[Export(("Date,Param")]
	public Godot.Object Date;
}
