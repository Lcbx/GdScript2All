using System;
using Godot;
using Godot.Collections;

public partial class Character : Godot.CharacterBody3D
{


	/* 3D character controller
	usable for both players and AI
	for players, input is handled an overlay script which sets local_dir and view_dir
	speed and acceleration is based on movementState which is a Ressource (see MovementState.gd)
	*/

	// TODO:
	// * add ways to get over obstacles
	// * implement fall damage
	// * hold crouch key to increase gravity ?
	// * hold jump key to lower gravity strength ?
	// * change gravity into a non-linear acceleration ?

	/* movement physics */

	public const double MIN_JUMP_VELOCITY = 3.5;
	public const double MAX_Y_SPEED = 10.0;

	public const Vector3 XZ = new Vector3(1.0, 0.0, 1.0);
	public const Vector3 YZ = new Vector3(0.0, 1.0, 1.0);
	public const Vector3 XY = new Vector3(1.0, 1.0, 0.0);

	public static double Gravity = 10.0;

	public Godot.Variant CoyoteTime = Utils.CreateTimer(this, 0.15);
	public Godot.Variant JumpCoolDown = Utils.CreateTimer(this, 0.15);


	protected override void _Process(double delta)
	{
		// in air
		if(!IsOnFloor())
		{
			Velocity.Y = Mathf.Clamp(Velocity.Y - Gravity * delta,  - MAX_Y_SPEED, MAX_Y_SPEED);
			MovementState = MovementEnum.fall;
		}
		else
		{
			// landing
			if(MovementState == MovementEnum.fall)
			{
				JumpCoolDown.Start();
				// TODO: apply fall damage + play landing animation
			}

			// on ground
			MovementState = WantedMovement;
			CoyoteTime.Start();
		}

		var ground_speed = CalculateGroundSpeed();

		// jump
		// TODO?: maybe add a special function to jump called on just_pressed
		if(GlobalMovDir.Y > 0.0 && !CoyoteTime.IsStopped() && JumpCoolDown.IsStopped())
		{
			Velocity.Y += Mathf.Max(MIN_JUMP_VELOCITY, ground_speed);
			CoyoteTime.Stop();
			EmitSignal("Jump", ground_speed);
		}

		// when running, always go forward 
		var direction = ( MovementState != MovementEnum.run ? GlobalMovDir : Basis.Z );

		var top_speed = Movements[MovementState].TopSpeed;
		var nimbleness = Movements[MovementState].Nimbleness;
		var acceleration = Movements[MovementState].Acceleration + ground_speed * nimbleness;

		var redirect = Mathf.Clamp(1.0 - nimbleness * delta, 0.0, 1.0);
		var vel_delta = acceleration * delta;

		Velocity.X = Mathf.MoveToward(Velocity.X * redirect, direction.X * top_speed, vel_delta);
		Velocity.Z = Mathf.MoveToward(Velocity.Z * redirect, direction.Z * top_speed, vel_delta);

		var new_ground_speed = CalculateGroundSpeed();

		EmitSignal("Movement", LocalDir, new_ground_speed);

		MoveAndSlide();

		foreach(int i in GD.Range(GetSlideCollisionCount()))
		{
			EmitSignal("Collision", GetSlideCollision(i));
		}
	}


	/* movement state / animations */

	[Signal]
	public delegate void ChangedStateEventHandler(MovementEnum state);
	[Signal]
	public delegate void CollisionEventHandler(Godot.KinematicCollision3D collision);
	[Signal]
	public delegate void MovementEventHandler(Vector3 dir, double speed);
	[Signal]
	public delegate void JumpEventHandler(double speed);

	public enum MovementEnum {crouch, walk, run, fall}
	[Export] public Array<MovementState> Movements;

	[Export]
	public Character.MovementEnum MovementState
	{
		set
		{
			if(_MovementState != value)
			{
				_MovementState = value;
				EmitSignal("ChangedState", _MovementState);
			}
		}
		get { return _MovementState; }
	}
	private Character.MovementEnum _MovementState = MovementEnum.walk;


	[Export]
	public Character.MovementEnum WantedMovement = MovementEnum.walk;


	/* steering variables */

	protected Vector3 _GlobalMovDir = new Vector3();
	[Export]
	public Vector3 GlobalMovDir
	{
		get
		{return _GlobalMovDir;
		}
		set
		{
			_GlobalMovDir = value;
			// TODO: verify up (y) is not inversed
			_LocalDir =  - value * Basis.Inverse();
		}
	}

	// NOTE: local_dir is normalized on the xz plane by Overlay
	protected Vector3 _LocalDir;
	[Export]
	public Vector3 LocalDir
	{
		get
		{return _LocalDir;
		}
		set
		{
			_LocalDir = value;
			_GlobalMovDir =  - value.X * Basis.X + value.Y * Vector3.Up + value.Z * Basis.Z;
		}
	}

	public double CalculateGroundSpeed()
	{
		return Mathf.Sqrt(Velocity.X * Velocity.X + Velocity.Z * Velocity.Z);
	}

	/* view */

	[Signal]
	public delegate void ViewDirChangedEventHandler(Vector3 euler);

	[Export]
	public Vector3 ViewDir
	{
		set
		{
			_ViewDir = value;
			_ViewDir.X = Mathf.Clamp(_ViewDir.X,  - Globals.ViewPitchLimit, Globals.ViewPitchLimit);
			EmitSignal("ViewDirChanged", _ViewDir);
		}
		get { return _ViewDir; }
	}
	private Vector3 _ViewDir = new Vector3();


}