using System;
using Godot;
using Dictionary = Godot.Collections.Dictionary;
using Array = Godot.Collections.Array;


// method to test statements
public partial class statements : Godot.Node
{
	public Array method()
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
		
		foreach(int j in range(i))
		{
			i += j;
		}
		
		switch(i)
		{
			case "1":
			{
				print(i);
				break;
			}
			case 1:
			{
				print(i);
				break;
			}
			case 0: if(true)
			{
				print("zero!");
				break;
			}
			//var x when false:
			//	print("unreachable")
			//[var x, var y] when true:
			//	print("array pattern")
			//{var x : var y} when true:
			//	print("dictionary pattern")
			default:
			{
				print("unknown");
				break;
			}
		}
		
		i += 3 / 3 + 2 * 0.5;
		
		await ToSignal(this, "jump");
		await ToSignal(get_tree(), "process_frame");
		
		get_tree().EmitSignal("process_frame", 0.7);
		get_tree().process_frame += something;
		
		return new Array{};;
	}
}