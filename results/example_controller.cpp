#include "Character.hpp"

void Character::_process(float delta)
{
	// in air
	if(!is_on_floor())
	{
		velocity.y = clampf(velocity.y - gravity * delta,  - MAX_Y_SPEED, MAX_Y_SPEED);
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
	
	Variant ground_speed = calculate_ground_speed();
	
	// jump
	// TODO?: maybe add a special function to jump called on just_pressed
	if(global_mov_dir.y > 0.0 && !coyoteTime.is_stopped() && jumpCoolDown.is_stopped())
	{
		velocity.y += maxf(MIN_JUMP_VELOCITY, ground_speed);
		coyoteTime.stop();
		jump.emit(ground_speed);
	}
	
	// when running, always go forward 
	Variant direction = ( movementState != MovementEnum.run ? global_mov_dir : basis.z );
	
	Variant top_speed = movements[movementState];
	Variant nimbleness = movements[movementState];
	Variant acceleration = movements[movementState] + ground_speed * nimbleness;
	
	float redirect = clampf(1.0 - nimbleness * delta, 0.0, 1.0);
	float vel_delta = acceleration * delta;
	
	velocity.x = move_toward(velocity.x * redirect, direction.x * top_speed, vel_delta);
	velocity.z = move_toward(velocity.z * redirect, direction.z * top_speed, vel_delta);
	
	Variant new_ground_speed = calculate_ground_speed();
	
	movement.emit(local_dir, new_ground_speed);
	
	move_and_slide();
	
	for(int i : range(get_slide_collision_count()))
	{
		collision.emit(get_slide_collision(i));
	}
}

void Character::set_movementState(Variant value)
{
	if(movementState != value)
	{
		movementState = value;
		emit_signal("changedState", movementState);
	}
}

Vector3 Character::get_global_mov_dir()
{return _global_mov_dir;
}

void Character::set_global_mov_dir(Vector3 value)
{
	_global_mov_dir = value;
	// TODO: verify up (y) is not inversed
	_local_dir =  - value * basis.inverse();
}

Vector3 Character::get_local_dir()
{return _local_dir;
}

void Character::set_local_dir(Vector3 value)
{
	_local_dir = value;
	_global_mov_dir =  - value.x * basis.x + value.y * Vector3::UP + value.z * basis.z;
}

float Character::calculate_ground_speed()
{
	return sqrt(velocity.x * velocity.x + velocity.z * velocity.z);
}

void Character::set_view_dir(Vector3 value)
{
	view_dir = value;
	view_dir.x = clampf(view_dir.x,  - Globals.view_pitch_limit, Globals.view_pitch_limit);
	emit_signal("viewDirChanged", view_dir);
}

void Character::set_movements(Array<MovementState> value) {
	movements = value;
}

Array<MovementState> Character::get_movements() {
	return movements;
}

static void Character::_bind_methods() {
	ClassDB::bind_method(D_METHOD("set_movementState", "value"), &Character::set_movementState);
	ClassDB::bind_method(D_METHOD("get_global_mov_dir"), &Character::get_global_mov_dir);
	ClassDB::bind_method(D_METHOD("set_global_mov_dir", "value"), &Character::set_global_mov_dir);
	ClassDB::bind_method(D_METHOD("get_local_dir"), &Character::get_local_dir);
	ClassDB::bind_method(D_METHOD("set_local_dir", "value"), &Character::set_local_dir);
	ClassDB::bind_method(D_METHOD("calculate_ground_speed"), &Character::calculate_ground_speed);
	ClassDB::bind_method(D_METHOD("set_view_dir", "value"), &Character::set_view_dir);
	ClassDB::bind_method(D_METHOD("set_movements", "value"), &Character::set_movements);
	ClassDB::bind_method(D_METHOD("get_movements"), &Character::get_movements);

	ADD_PROPERTY(PropertyInfo(Variant::OBJECT, "movements"), "set_movements", "get_movements");
	ADD_SIGNAL(MethodInfo("changedState", PropertyInfo(Variant::OBJECT, "state")));
	ADD_SIGNAL(MethodInfo("collision", PropertyInfo(Variant::OBJECT, "collision")));
	ADD_SIGNAL(MethodInfo("movement", PropertyInfo(Variant::VECTOR3, "dir"), PropertyInfo(Variant::FLOAT, "speed")));
	ADD_SIGNAL(MethodInfo("jump", PropertyInfo(Variant::FLOAT, "speed")));
	ADD_SIGNAL(MethodInfo("viewDirChanged", PropertyInfo(Variant::VECTOR3, "euler")));
}

