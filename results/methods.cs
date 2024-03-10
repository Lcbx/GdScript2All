using System;
using Godot;
using Godot.Collections;


public partial class methods : Godot.Node
{
	public void Empty()
	{
	}

	public void Reassign()
	{
		reassign += 2;
	}

	public void Assign()
	{
		assign = 2;
	}

	//test1
	public double Init(double v = 1.0)
	{//test2
		//test3
		Returning(7.0);
		//test4
	}

	public double Returning(double v)
	{
		Empty();
		return 1.0;
	}

	public void Declare()
	{
		var declare = 2;
	}

	public double ReturnInference(double param = 5.0)
	{
		var val = 2;
		return val * param;
	}

}