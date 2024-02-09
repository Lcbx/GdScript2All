using System;
using Godot;
using Dictionary = Godot.Collections.Dictionary;
using Array = Godot.Collections.Array;


public partial class test5 : Godot.Node
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
	
	
	public double init(double v = 1.0)
	{
		returning(7.0);
	}
	
	public double returning(double v)
	{
		empty();
		return 1.0;
	}
	
	public void declare()
	{
		var declare = 2
	}
	
	public void funcception()
	{
		func;hi();;
		//PANIC! <:> unexpected at Token(type=':', value=':', lineno=23, index=249, end=250)//PANIC! <pass> unexpected at Token(type='EOF', value='EOF', lineno=24, index=253, end=257)
	}