using System;
using Godot;
using Godot.Collections;


[Tool]
public partial class MovementState : Godot.Resource
{


	//# acceleration apllied towward chosen direction
	[Export] public double Acceleration;
	//# redirects a % current velocity toward chosen direction
	[Export] public double Nimbleness;
	//# maximum achievable velocity 
	[Export] public double TopSpeed;


}