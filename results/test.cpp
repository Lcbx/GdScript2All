#include "test.hpp"
#include <godot_cpp/core/class_db.hpp>


static void Nested1::_bind_methods() {
}

float test::method(float param)
{
	int val = 2;
	for(string k : string_array)
	{
		print(k);
	}
	return val * param;
}

void test::set_getset_var2(float value)
{
	getset_var2 = value;
}

float test::get_getset_var2()
{
	return getset_var2;
}

void test::async_function()
{
	/* await self.jump; */ // no equivalent to await in c++ !
	/* await get_tree().process_frame; */ // no equivalent to await in c++ !
	
	get_tree().emit_signal("process_frame", 0.7);
	
	Callable myLambda = () =>
	{	print("look ma i'm jumping");
	};
	
	// lambdas are not perfectly translated
	connect("jump", myLambda);
	
	emit_signal("movement", Vector3::UP, 0.1);
}

void test::_ready()
{
	k = 42;
}

void test::set_export(Variant value){
	export = value;
}

Variant test::get_export(){
	 return export;
}

void test::set_export_param(Variant value){
	export_param = value;
}

Variant test::get_export_param(){
	 return export_param;
}

void test::set_export_flags(Variant value){
	export_flags = value;
}

Variant test::get_export_flags(){
	 return export_flags;
}

static void test::_bind_methods() {
	ADD_PROPERTY(PropertyInfo(Variant::OBJECT, "export"), "set_export", "get_export");
	ADD_PROPERTY(PropertyInfo(Variant::OBJECT, "export_param"), "set_export_param", "get_export_param");
	ADD_PROPERTY(PropertyInfo(Variant::OBJECT, "export_flags", PROPERTY_HINT_FLAGS, "Self:4,Allies:8,Foes:16"), "set_export_flags", "get_export_flags");
	ADD_SIGNAL(MethodInfo("jump"));
	ADD_SIGNAL(MethodInfo("movement", PropertyInfo(Variant::VECTOR3, "dir"), PropertyInfo(Variant::FLOAT, "speed")));
	ClassDB::bind_method(D_METHOD("method", "param"), &test::method);
	ClassDB::bind_method(D_METHOD("set_getset_var2", "value"), &test::set_getset_var2);
	ClassDB::bind_method(D_METHOD("get_getset_var2"), &test::get_getset_var2);
	ClassDB::bind_method(D_METHOD("async_function"), &test::async_function);
	ClassDB::bind_method(D_METHOD("set_export", "value"), &test::set_export);
	ClassDB::bind_method(D_METHOD("get_export"), &test::get_export);
	ClassDB::bind_method(D_METHOD("set_export_param", "value"), &test::set_export_param);
	ClassDB::bind_method(D_METHOD("get_export_param"), &test::get_export_param);
	ClassDB::bind_method(D_METHOD("set_export_flags", "value"), &test::set_export_flags);
	ClassDB::bind_method(D_METHOD("get_export_flags"), &test::get_export_flags);
}

