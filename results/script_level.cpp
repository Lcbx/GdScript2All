#include "script_level.hpp"
#include <godot_cpp/core/class_db.hpp>

static void Nested1::_bind_methods() {

}

static void Nested2::_bind_methods() {

}

static void Nested3::_bind_methods() {

}

static void Nested4::_bind_methods() {

}

float script_level::get_get_var3()
{return get_var3;
}

 void script_level::set_DEF(float value)
{
	set_sprite_offset(value);
}

float script_level::get_DEF()
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

static void script_level::_bind_methods() {
	ClassDB::bind_method(D_METHOD("get_get_var3"), &script_level::get_get_var3);
	ClassDB::bind_method(D_METHOD("set_DEF", "value"), &script_level::set_DEF);
	ClassDB::bind_method(D_METHOD("get_DEF"), &script_level::get_DEF);
	ClassDB::bind_method(D_METHOD("set_export", "value"), &script_level::set_export);
	ClassDB::bind_method(D_METHOD("get_export"), &script_level::get_export);
	ClassDB::bind_method(D_METHOD("set_export_param", "value"), &script_level::set_export_param);
	ClassDB::bind_method(D_METHOD("get_export_param"), &script_level::get_export_param);
	ClassDB::bind_method(D_METHOD("set_export_flags", "value"), &script_level::set_export_flags);
	ClassDB::bind_method(D_METHOD("get_export_flags"), &script_level::get_export_flags);

	ADD_PROPERTY(PropertyInfo(Variant::OBJECT, "export"), "set_export", "get_export");
	ADD_GROUP("with parameters","");
	ADD_PROPERTY(PropertyInfo(Variant::OBJECT, "export_param"), "set_export_param", "get_export_param");
	ADD_CATEGORY("category","");
	ADD_PROPERTY(PropertyInfo(Variant::OBJECT, "export_flags", PROPERTY_HINT_FLAGS, "Self:4,Allies:8,Foes:16"), "set_export_flags", "get_export_flags");
	ADD_GROUP("group","");
	ADD_SUBGROUP("subgroup","");
	ADD_PROPERTY(PropertyInfo(Variant::FLOAT, "get_var3"), "set_get_var3", "get_get_var3");
	ADD_SIGNAL(MethodInfo("a"));
	ADD_SIGNAL(MethodInfo("b", PropertyInfo(Variant::INT, "c"), PropertyInfo(Variant::OBJECT, "d")));
}

