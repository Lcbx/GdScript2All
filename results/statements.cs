using System;
using Godot;
using Dictionary = Godot.Collections.Dictionary;
using Array = Godot.Collections.Array;


public partial class statements : Godot.Node
{
	// method to test statements
	public void method()
	{
		
		
		
		var i = 0;
		
		if(ABC)
		{
			assert(false);
		}
		else if(false)
		{
			print("Hello" + " " + "World");
		}
		else if(true)
		{
			print("Goodbye ","World");
		}
		else
		{
			print(i);
		}
		
		while(false)
		{
			i += 1;
			break;
			continue;
		}
		
		foreach(Variant j in range(i))
		{
			i += j;
		}
		
		i;;
		//PANIC! <:> unexpected at Token(type=':', value=':', lineno=27, index=291, end=292)
		//PANIC! <1 :> unexpected at Token(type='STRING', value='1', lineno=28, index=295, end=298)
	}
}