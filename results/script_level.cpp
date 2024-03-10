
#include "script_level.hpp"

#include <godot_cpp/core/object.hpp>
#include <godot_cpp/core/class_db.hpp>
#include <godot_cpp/variant/utility_functions.hpp>

double script_level::get_get_var3()
{return get_var3;
}

void script_level::set_get_var3(double value) {
	get_var3 = value;
}

 void script_level::set_DEF(double value)
{
	set_sprite_offset(value);
}

double script_level::get_DEF()
{
	return sprite_offset;
}

void script_level::_ready()
{
	getset_var = 0.0;
}

void script_level::set_export(Variant value) {
	export = value;
}

Variant script_level::get_export() {
	return export;
}

void script_level::set_export_param(Variant value) {
	export_param = value;
}

Variant script_level::get_export_param() {
	return export_param;
}

void script_level::set_export_flags(Variant value) {
	export_flags = value;
}

Variant script_level::get_export_flags() {
	return export_flags;
}

void script_level::_bind_methods() {
	ClassDB::bind_method(D_METHOD("get_get_var3"), &script_level::get_get_var3);
	ClassDB::bind_method(D_METHOD("set_get_var3", "value"), &script_level::set_get_var3);
	ClassDB::bind_method(D_METHOD("set_DEF", "value"), &script_level::set_DEF);
	ClassDB::bind_method(D_METHOD("get_DEF"), &script_level::get_DEF);
	ClassDB::bind_method(D_METHOD("set_export", "value"), &script_level::set_export);
	ClassDB::bind_method(D_METHOD("get_export"), &script_level::get_export);
	ClassDB::bind_method(D_METHOD("set_export_param", "value"), &script_level::set_export_param);
	ClassDB::bind_method(D_METHOD("get_export_param"), &script_level::get_export_param);
	ClassDB::bind_method(D_METHOD("set_export_flags", "value"), &script_level::set_export_flags);
	ClassDB::bind_method(D_METHOD("get_export_flags"), &script_level::get_export_flags);
	ClassDB::bind_integer_constant(get_class_static(), _gde_constant_get_enum_name(UNIT_NEUTRAL, "UNIT_NEUTRAL"), "UNIT_NEUTRAL", UNIT_NEUTRAL);
	ClassDB::bind_integer_constant(get_class_static(), _gde_constant_get_enum_name(UNIT_ENEMY, "UNIT_ENEMY"), "UNIT_ENEMY", UNIT_ENEMY);
	ClassDB::bind_integer_constant(get_class_static(), _gde_constant_get_enum_name(UNIT_ALLY, "UNIT_ALLY"), "UNIT_ALLY", UNIT_ALLY);
	ClassDB::bind_integer_constant(get_class_static(), _gde_constant_get_enum_name(THING_1, "THING_1"), "THING_1", THING_1);
	ClassDB::bind_integer_constant(get_class_static(), _gde_constant_get_enum_name(THING_2, "THING_2"), "THING_2", THING_2);
	ClassDB::bind_integer_constant(get_class_static(), _gde_constant_get_enum_name(ANOTHER_THING, "ANOTHER_THING"), "ANOTHER_THING", ANOTHER_THING);
	ClassDB::add_property(get_class_static(), PropertyInfo(Variant::OBJECT, "export"), "set_export", "get_export");
	ClassDB::add_property_group(get_class_static(), "with parameters","");
	ClassDB::add_property(get_class_static(), PropertyInfo(Variant::OBJECT, "export_param"), "set_export_param", "get_export_param");
	ClassDB::add_property_category(get_class_static(), "category","");
	ClassDB::add_property(get_class_static(), PropertyInfo(Variant::OBJECT, "export_flags", PROPERTY_HINT_FLAGS, "Self:4,Allies:8,Foes:16"), "set_export_flags", "get_export_flags");
	ClassDB::add_property_group(get_class_static(), "group","");
	ClassDB::add_property_subgroup(get_class_static(), "subgroup","");
	ClassDB::add_property(get_class_static(), PropertyInfo(Variant::FLOAT, "get_var3"), "set_get_var3", "get_get_var3");
	ClassDB::add_signal(get_class_static(), MethodInfo("a"));
	ClassDB::add_signal(get_class_static(), MethodInfo("b", PropertyInfo(Variant::INT, "c"), PropertyInfo(Variant::OBJECT, "d")));
}

