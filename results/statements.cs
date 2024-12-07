using Godot;
using Godot.Collections;


// method to test statements
[GlobalClass]
public partial class statements : Godot.Node
{
	public Array Method()
	{


		var i = 0;

		if(true)
		{
			System.Diagnostics.Debug.Assert(false);
		}
		else if(false)
		{
			GD.Convert("Hello" + " " + "World", typeof(string));
		}
		else if(true)
		{
			GD.Print("Goodbye ", "World");
		}
		else
		{
			GD.Print(System.Environment.StackTrace());
		}

		while(false)
		{
			i += 1;

			// unindented comment
			break;
			continue;
		}

		foreach(int j in GD.Range(i))
		{
			i += j;
		}

		foreach(Variant j in array)
		{
			i += j;
		}

		if(i is int)
		{i = 0;
		}
		GD.Print(i is Godot.MeshInstance3D);

		switch(i)
		{
			case "1":
			{
				GD.Print(i);
				break; }
			case 1:
			{
				GD.Print(i);
				break; }
			case 0: if(true)
			{
				GD.Print("zero!");

				//var x when false:
				//	print("unreachable")
				//[var x, var y] when true:
				//	print("array pattern")
				//{var x : var y} when true:

				break; }//	print("dictionary pattern")
			default:
			{
				GD.Print("unknown");
				break; }
		}

		i += 3 / 3 + 2 * 0.5;

		await ToSignal(this, "Jump");
		await ToSignal(GetTree(), "ProcessFrame");

		GetTree().EmitSignal("ProcessFrame", 0.7);
		GetTree().ProcessFrame += something;

		return new Array{};
	}


}