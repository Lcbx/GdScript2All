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
	
	public const Godot.Vector3 XZ = new Vector3(1.0,0.0,1.0);
	public const Godot.Vector3 YZ = new Vector3(0.0,1.0,1.0);
	public const Godot.Vector3 XY = new Vector3(1.0,1.0,0.0);
	
	public static Godot.Variant gravity = Godot.ProjectSettings.get_setting("physics/3d/default_gravity");
	
	public Godot.Variant coyoteTime = Utils.createTimer(this,0.15);
	public Godot.Variant jumpCoolDown = Utils.createTimer(this,0.15);
	
	
	protected void _process(double delta)
	{
		// in air
		if(!is_on_floor())
		{
			velocity.y = Mathf.Clamp(velocity.y - gravity * delta, - MAX_Y_SPEED,MAX_Y_SPEED);
			movementState = MovementEnum.fall;
		}
		else
		{
			// landing
			if(movementState == MovementEnum.fall)
			{
				jumpCoolDown.start();
				// TODO: apply fall damage + play landing animation
			}
			
			// on ground
			movementState = wantedMovement;
			coyoteTime.start();
		}
		
		var ground_speed = calculate_ground_speed();
		
		// jump
		// TODO?: maybe add a special function to jump called on just_pressed
		if(global_mov_dir.y > 0.0 && !coyoteTime.is_stopped() && jumpCoolDown.is_stopped())
		{
			velocity.y += Mathf.Max(MIN_JUMP_VELOCITY,ground_speed);
			coyoteTime.stop();
			jump.emit(ground_speed);
		}
		
		// when running, always go forward 
		var direction = ( movementState != MovementEnum.run ? global_mov_dir : basis.z );
		
		var top_speed = movements[movementState];
		var nimbleness = movements[movementState];
		var acceleration = movements[movementState] + ground_speed * nimbleness;
		
		var redirect = Mathf.Clamp(1.0 - nimbleness * delta,0.0,1.0);
		var vel_delta = acceleration * delta;
		
		velocity.x = Mathf.MoveToward(velocity.x * redirect,direction.x * top_speed,vel_delta);
		velocity.z = Mathf.MoveToward(velocity.z * redirect,direction.z * top_speed,vel_delta);
		
		var new_ground_speed = calculate_ground_speed();
		
		movement.emit(local_dir,new_ground_speed);
		
		move_and_slide();
		
		foreach(int i in range(get_slide_collision_count()))
		{
			collision.emit(get_slide_collision(i));
		}
	}
	
	
	/* movement state / animations */
	
	[Signal]
	public delegate void changedStateHandler(MovementEnum state);
	[Signal]
	public delegate void collisionHandler(Godot.KinematicCollision3D collision);
	[Signal]
	public delegate void movementHandler(Godot.Vector3 dir,double speed);
	[Signal]
	public delegate void jumpHandler(double speed);
	
	public enum MovementEnum {crouch,walk,run,fall}
	[Export]
	public Array<MovementState> movements;
	
	public Godot.Variant movementState = MovementEnum.walk
	{
		set
		{
			if(_movementState != value)
			{
				_movementState = value;
				EmitSignal("changedState", _movementState);
			}
		}
	}
	private Godot.Variant _movementState;

	
	public Godot.Variant wantedMovement = MovementEnum.walk;
	
	
	/* steering variables */
	
	protected Godot.Vector3 _global_mov_dir = new Vector3();
	public Godot.Vector3 global_mov_dir = new Vector3()
	{
		get
		{return _global_mov_dir;
		}
		set
		{
			_global_mov_dir = value;
			// TODO: verify up (y) is not inversed
			_local_dir =  - value * basis.inverse();
		}
	}
	
	// NOTE: local_dir is normalized on the xz plane by Overlay
	protected Godot.Vector3 _local_dir;
	public Godot.Vector3 local_dir
	{
		get
		{return _local_dir;
		}
		set
		{
			_local_dir = value;
			_global_mov_dir =  - value.x * basis.x + value.y * Godot.Vector3.UP + value.z * basis.z;
		}
	}
	
	public double calculate_ground_speed()
	{
		return Mathf.Sqrt(velocity.x * velocity.x + velocity.z * velocity.z);
	}
	
	/* view */
	
	[Signal]
	public delegate void viewDirChangedHandler(Godot.Vector3 euler);
	
	public Godot.Vector3 view_dir = new Vector3()
	{
		set
		{
			_view_dir = value;
			_view_dir.x = Mathf.Clamp(_view_dir.x, - Globals.view_pitch_limit,Globals.view_pitch_limit);
			EmitSignal("viewDirChanged", _view_dir);
		}
	}
	private Godot.Vector3 _view_dir;

	
	
}