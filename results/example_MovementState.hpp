
#ifndef EXAMPLE_MOVEMENTSTATE_H
#define EXAMPLE_MOVEMENTSTATE_H

#include <godot_cpp/godot.hpp>
#include <godot_cpp/variant/array.hpp>
#include <godot_cpp/variant/dictionary.hpp>
#include <godot_cpp/classes/resource.hpp>

using namespace godot;

class MovementState : public Resource {
	GDCLASS(MovementState, Resource);
public:

//# acceleration apllied towward chosen direction

protected:
	double acceleration;
//# redirects a % current velocity toward chosen direction
	double nimbleness;
//# maximum achievable velocity 
	double top_speed;

public:
	void set_acceleration(double value);
	double get_acceleration();
	void set_nimbleness(double value);
	double get_nimbleness();
	void set_top_speed(double value);
	double get_top_speed();

	static void _bind_methods();
};

#endif // EXAMPLE_MOVEMENTSTATE_H
