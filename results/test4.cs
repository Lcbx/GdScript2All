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
	public const string string = "the fox said \"get off my lawn\"";
	public int int = 0;
	protected bool _bool = True;
	
	[Export]
	
	public Array array = new Array{0,1,2,};
	
	[Export("param1, param2")]
	
	public Dictionary dict = new Dictionary{{0,1},{1,2},{2,3},};
	
	[Export(PropertyHint.Flags,"Self:4, Allies:8, Foes:16")]
	
	public int parenthesis = (42);
	
	public Godot.Object preload_resource = preload();
	public Godot.Object load_resource = load();
	
	public Godot.Object get_node = ;
}
