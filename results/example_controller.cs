using System;
using Godot;
using Dictionary = Godot.Collections.Dictionary;
using Array = Godot.Collections.Array;

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

	public const Godot.Vector3 XZ = new Vector3(1.0, 0.0, 1.0);
	public const Godot.Vector3 YZ = new Vector3(0.0, 1.0, 1.0);
	public const Godot.Vector3 XY = new Vector3(1.0, 1.0, 0.0);

	public static Godot.Variant Gravity = Godot.ProjectSettings.GetSetting("physics/3d/default_gravity");

	public Godot.Variant CoyoteTime = Utils.CreateTimer(this, 0.15);
	public Godot.Variant JumpCoolDown = Utils.CreateTimer(this, 0.15);


	protected override void _Process(double delta)
	{
		// in air
		if(!IsOnFloor())
		{
			Velocity.Y = Mathf.Clamp(Velocity.Y - Gravity * delta,  - MAX_Y_SPEED, MAX_Y_SPEED);
			movementState = MovementEnum.Fall;
		}
		else
		{
			// landing
			if(movementState == MovementEnum.Fall)
			{
				JumpCoolDown.Start();
				// TODO: apply fall damage + play landing animation
			}

			// on ground
			movementState = wantedMovement;
			CoyoteTime.Start();
		}

		var ground_speed = CalculateGroundSpeed();

		// jump
		// TODO?: maybe add a special function to jump called on just_pressed
		if(global_mov_dir.Y > 0.0 && !CoyoteTime.IsStopped() && JumpCoolDown.IsStopped())
		{
			Velocity.Y += Mathf.Max(MIN_JUMP_VELOCITY, ground_speed);
			CoyoteTime.Stop();
			jump.Emit(ground_speed);
		}

		// when running, always go forward 
		var direction = ( movementState != MovementEnum.Run ? global_mov_dir : Basis.Z );

		var top_speed = movements[movementState].TopSpeed;
		var nimbleness = movements[movementState].Nimbleness;
		var acceleration = movements[movementState].Acceleration + ground_speed * nimbleness;

		var redirect = Mathf.Clamp(1.0 - nimbleness * delta, 0.0, 1.0);
		var vel_delta = acceleration * delta;

		Velocity.X = Mathf.MoveToward(Velocity.X * redirect, direction.X * top_speed, vel_delta);
		Velocity.Z = Mathf.MoveToward(Velocity.Z * redirect, direction.Z * top_speed, vel_delta);

		var new_ground_speed = CalculateGroundSpeed();

		movement.Emit(local_dir, new_ground_speed);

		MoveAndSlide();

		foreach(int i in Range(GetSlideCollisionCount()))
		{
			collision.Emit(GetSlideCollision(i));
		}
	}


	/* movement state / animations */

	[Signal]
	public delegate void ChangedStateHandler(MovementEnum state);
	[Signal]
	public delegate void CollisionHandler(Godot.KinematicCollision3D collision);
	[Signal]
	public delegate void MovementHandler(Godot.Vector3 dir, double speed);
	[Signal]
	public delegate void JumpHandler(double speed);

	public enum MovementEnum {crouch, walk, run, fall}
	[Export] public Array<MovementState> Movements;

	public Godot.Variant MovementState = MovementEnum.Walk
	{
		set
		{
			if(_MovementState != value)
			{
				_MovementState = value;
				EmitSignal("changedState", _MovementState);
			}
		}
	}
	private Godot.Variant _MovementState;


	public Godot.Variant WantedMovement = MovementEnum.Walk;


	/* steering variables */

	protected Godot.Vector3 _GlobalMovDir = new Vector3();
	public Godot.Vector3 GlobalMovDir = new Vector3()
	{
		get
		{return _GlobalMovDir;
		}
		set
		{
			_GlobalMovDir = value;
			// TODO: verify up (y) is not inversed
			_local_dir =  - value * Basis.Inverse();
		}
	}

	// NOTE: local_dir is normalized on the xz plane by Overlay
	protected Godot.Vector3 _LocalDir;
	public Godot.Vector3 LocalDir
	{
		get
		{return _LocalDir;
		}
		set
		{
			_LocalDir = value;
			_GlobalMovDir =  - value.X * Basis.X + value.Y * Vector3.UP + value.Z * Basis.Z;
		}
	}

	public double CalculateGroundSpeed()
	{
		return Mathf.Sqrt(Velocity.X * Velocity.X + Velocity.Z * Velocity.Z);
	}

	/* view */

	[Signal]
	public delegate void ViewDirChangedHandler(Godot.Vector3 euler);

	public Godot.Vector3 ViewDir = new Vector3()
	{
		set
		{
			_ViewDir = value;
			_ViewDir.X = Mathf.Clamp(_ViewDir.X,  - Globals.ViewPitchLimit, Globals.ViewPitchLimit);
			EmitSignal("viewDirChanged", _ViewDir);
		}
	}
	private Godot.Vector3 _ViewDir;


}