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
			velocity.y = clampf(velocity.y - gravity * delta, - MAX_Y_SPEED,MAX_Y_SPEED);
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
			velocity.y += maxf(MIN_JUMP_VELOCITY,ground_speed);
			coyoteTime.stop();
			jump.emit(ground_speed);
		}
		
		// when running, always go forward 
		var direction = ( movementState ? global_mov_dir : ! ); = MovementEnum.run;else;basis.z;
		
		var top_speed = movements[movementState];
		var nimbleness = movements[movementState];
		var acceleration = movements[movementState] + ground_speed * nimbleness;
		
		var redirect = clampf(1.0 - nimbleness * delta,0.0,1.0);
		var vel_delta = acceleration * delta;
		
		velocity.x = move_toward(velocity.x * redirect,direction.x * top_speed,vel_delta);
		velocity.z = move_toward(velocity.z * redirect,direction.z * top_speed,vel_delta);
		
		var new_ground_speed = calculate_ground_speed();
		
		movement.emit(local_dir,new_ground_speed);
		
		move_and_slide();
		
		foreach(Variant i in range(get_slide_collision_count()))
		{
			collision.emit(get_slide_collision(i));
		}
	}
	
	
	/* movement state / animations */
	
	
	//PANIC! <signal changedState ( state : MovementEnum )> unexpected at Token(type='TEXT', value='signal', lineno=83, index=2393, end=2399)
	//PANIC! <signal collision ( collision : KinematicCollision3D )> unexpected at Token(type='TEXT', value='signal', lineno=84, index=2435, end=2441)
}