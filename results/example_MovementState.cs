using System;
using Godot;
using Dictionary = Godot.Collections.Dictionary;
using Array = Godot.Collections.Array;


[Tool]
public partial class MovementState : Godot.Resource
{
	
	
	//# acceleration apllied towward chosen direction
	[Export]
	public double acceleration;
	//# redirects a % current velocity toward chosen direction
	[Export]
	public double nimbleness;
	//# maximum achievable velocity 
	[Export]
	public double top_speed;
	
}