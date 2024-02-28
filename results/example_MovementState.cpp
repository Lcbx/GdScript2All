#include "MovementState.hpp"
#include <godot_cpp/core/class_db.hpp>

void MovementState::set_acceleration(float value) {
	acceleration = value;
}

float MovementState::get_acceleration() {
	return acceleration;
}

void MovementState::set_nimbleness(float value) {
	nimbleness = value;
}

float MovementState::get_nimbleness() {
	return nimbleness;
}

void MovementState::set_top_speed(float value) {
	top_speed = value;
}

float MovementState::get_top_speed() {
	return top_speed;
}

static void MovementState::_bind_methods() {
	ClassDB::bind_method(D_METHOD("set_acceleration", "value"), &MovementState::set_acceleration);
	ClassDB::bind_method(D_METHOD("get_acceleration"), &MovementState::get_acceleration);
	ClassDB::bind_method(D_METHOD("set_nimbleness", "value"), &MovementState::set_nimbleness);
	ClassDB::bind_method(D_METHOD("get_nimbleness"), &MovementState::get_nimbleness);
	ClassDB::bind_method(D_METHOD("set_top_speed", "value"), &MovementState::set_top_speed);
	ClassDB::bind_method(D_METHOD("get_top_speed"), &MovementState::get_top_speed);

	ADD_PROPERTY(PropertyInfo(Variant::FLOAT, "acceleration"), "set_acceleration", "get_acceleration");
	ADD_PROPERTY(PropertyInfo(Variant::FLOAT, "nimbleness"), "set_nimbleness", "get_nimbleness");
	ADD_PROPERTY(PropertyInfo(Variant::FLOAT, "top_speed"), "set_top_speed", "get_top_speed");
}

