using System;
using Godot;
using Dictionary = Godot.Collections.Dictionary;
using Array = Godot.Collections.Array;


public partial class methods : Godot.Node
{
	public void empty()
	{
	}
	
	public void reassign()
	{
		reassign += 2;
	}
	
	public void assign()
	{
		assign = 2;
	}
	
	//test1
	public double init(double v = 1.0)
	{//test2
		//test3
		returning(7.0);
		//test4
	}
	
	public double returning(double v)
	{
		empty();
		return 1.0;
	}
	
	public void declare()
	{
		var declare = 2;
	}
	
	public double return_inference(double param = 5.0)
	{
		var val = 2;
		return val * param;;
	}
}