
#ifndef MOVEMENTSTATE_H
#define MOVEMENTSTATE_H

// default includes
#include <godot_cpp/godot.hpp>
#include <godot_cpp/core/object.hpp>
#include <godot_cpp/core/class_db.hpp>

using namespace godot;

namespace godot {

class MovementState : public Resource {
	GDCLASS(MovementState, Resource);
public:

//# acceleration apllied towward chosen direction

protected:
	float acceleration;
//# redirects a % current velocity toward chosen direction
	float nimbleness;
//# maximum achievable velocity 
	float top_speed;

public:
	void set_acceleration(float value);
	float get_acceleration();
	void set_nimbleness(float value);
	float get_nimbleness();
	void set_top_speed(float value);
	float get_top_speed();

	static void _bind_methods();
}

}

#endif // MOVEMENTSTATE_H
