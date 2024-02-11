using System;
using Godot;
using Dictionary = Godot.Collections.Dictionary;
using Array = Godot.Collections.Array;


public partial class statements : Godot.Node
{
	// method to test statements
	public void method()
	{
		
		
		
		var i = 0
		
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
		}
		
		j;in;range(i);;
		//PANIC! <:> unexpected at Token(type=':', value=':', lineno=22, index=251, end=252)
		
		//PANIC! <i += j> unexpected at Token(type='TEXT', value='i', lineno=23, index=255, end=256)
	}
}