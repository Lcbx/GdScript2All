using System;
using Godot;
using Dictionary = Godot.Collections.Dictionary;
using Array = Godot.Collections.Array;



// line comment

/* multiline
   comment
*/

[Tool]
public partial class test4 : Godot.Node
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
	enum Enum0 {UNIT_NEUTRAL, UNIT_ENEMY, UNIT_ALLY}
	enum Named {THING_1, THING_2, ANOTHER_THING = -1}
	
	public Godot.Object foo;
	
	protected const int _i = 0;
	
	[Export(("Date,Param")]
	
	public bool ABC = True;
	
	[Export(PropertyHint.Flags,("Self:4, Allies:8, Foes:16")]
	
	public Godot.Array a = ;
}
