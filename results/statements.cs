using System;
using Godot;
using Dictionary = Godot.Collections.Dictionary;
using Array = Godot.Collections.Array;


// method to test statements
public partial class statements : Godot.Node
{
	public Array Method()
	{
		
		
		
		var i = 0;
		
		if(ABC)
		{
			Assert(false);
		}
		else if(false)
		{
			GD.Print("Hello" + " " + "World");
		}
		else if(true)
		{
			GD.Print("Goodbye ", "World");
		}
		else
		{
			GD.Print(i);
		}
		
		while(false)
		{
			i += 1;
			break;
			continue;
		}
		
		foreach(int j in Range(i))
		{
			i += j;
		}
		
		switch(i)
		{
			case "1":
			{
				GD.Print(i);
				break;
			}
			case 1:
			{
				GD.Print(i);
				break;
			}
			case 0: if(true)
			{
				GD.Print("zero!");
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
				GD.Print("unknown");
				break;
			}
		}
		
		i += 3 / 3 + 2 * 0.5;
		
		await ToSignal(this, "jump");
		await ToSignal(GetTree(), "ProcessFrame");
		
		GetTree().EmitSignal("process_frame", 0.7);
		GetTree().process_frame += something;
		
		return new Array{};;
	}
}