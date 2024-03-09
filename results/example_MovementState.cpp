
#include "example_MovementState.hpp"

#include <godot_cpp/core/object.hpp>
#include <godot_cpp/core/class_db.hpp>
#include <godot_cpp/variant/utility_functions.hpp>

void MovementState::set_acceleration(double value) {
	acceleration = value;
}

double MovementState::get_acceleration() {
	return acceleration;
}

void MovementState::set_nimbleness(double value) {
	nimbleness = value;
}

double MovementState::get_nimbleness() {
	return nimbleness;
}

void MovementState::set_top_speed(double value) {
	top_speed = value;
}

double MovementState::get_top_speed() {
	return top_speed;
}

void MovementState::_bind_methods() {
	ClassDB::bind_method(D_METHOD("set_acceleration", "value"), &MovementState::set_acceleration);
	ClassDB::bind_method(D_METHOD("get_acceleration"), &MovementState::get_acceleration);
	ClassDB::bind_method(D_METHOD("set_nimbleness", "value"), &MovementState::set_nimbleness);
	ClassDB::bind_method(D_METHOD("get_nimbleness"), &MovementState::get_nimbleness);
	ClassDB::bind_method(D_METHOD("set_top_speed", "value"), &MovementState::set_top_speed);
	ClassDB::bind_method(D_METHOD("get_top_speed"), &MovementState::get_top_speed);

	ClassDB::add_property(get_class_static(), PropertyInfo(Variant::FLOAT, "acceleration"), "set_acceleration", "get_acceleration");
	ClassDB::add_property(get_class_static(), PropertyInfo(Variant::FLOAT, "nimbleness"), "set_nimbleness", "get_nimbleness");
	ClassDB::add_property(get_class_static(), PropertyInfo(Variant::FLOAT, "top_speed"), "set_top_speed", "get_top_speed");
}

