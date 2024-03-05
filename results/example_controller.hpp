
#ifndef EXAMPLE_CONTROLLER_H
#define EXAMPLE_CONTROLLER_H

#include <godot_cpp/godot.hpp>

using namespace godot;

namespace godot {

class Character : public CharacterBody3D {
	GDCLASS(Character, CharacterBody3D);
public:

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

protected:
	const float MIN_JUMP_VELOCITY = 3.5;
	const float MAX_Y_SPEED = 10.0;

	const Vector3 XZ = Vector3(1.0, 0.0, 1.0);
	const Vector3 YZ = Vector3(0.0, 1.0, 1.0);
	const Vector3 XY = Vector3(1.0, 1.0, 0.0);

	static Variant gravity = ProjectSettings::get_singleton()->get_setting("physics/3d/default_gravity");

	Variant coyoteTime = Utils.createTimer(self, 0.15);
	Variant jumpCoolDown = Utils.createTimer(self, 0.15);

/* movement state / animations */

public:
	void _process(float delta) override;
	/* signal changedState(MovementEnum* state) */
	/* signal collision(KinematicCollision3D* collision) */
	/* signal movement(Vector3 dir, float speed) */
	/* signal jump(float speed) */

	enum MovementEnum {crouch,walk,run,fall};

protected:
	Array<MovementState> movements;

	Variant movementState = MovementEnum.walk;

public:
	void set_movementState(Variant value);

protected:
	Variant wantedMovement = MovementEnum.walk;

/* steering variables */

	Vector3 _global_mov_dir = Vector3();
	Vector3 global_mov_dir = Vector3();

public:
	Vector3 get_global_mov_dir();

// NOTE: local_dir is normalized on the xz plane by Overlay
	void set_global_mov_dir(Vector3 value);

protected:
	Vector3 _local_dir;
	Vector3 local_dir;

public:
	Vector3 get_local_dir();

	void set_local_dir(Vector3 value);

/* view */

	float calculate_ground_speed();
	/* signal viewDirChanged(Vector3 euler) */

protected:
	Vector3 view_dir = Vector3();

public:
	void set_view_dir(Vector3 value);
	void set_movements(Array<MovementState> value);
	Array<MovementState> get_movements();

	static void _bind_methods();
}

}

#endif // EXAMPLE_CONTROLLER_H
