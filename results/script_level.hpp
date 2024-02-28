
#ifndef SCRIPT_LEVEL_H
#define SCRIPT_LEVEL_H

#include <godot_cpp/godot.hpp>

using namespace godot;

namespace godot {

class Nested1 : public test {
	GDCLASS(Nested1, test);
public:

	static void _bind_methods();
}

class Nested3 : public Object {
	GDCLASS(Nested3, Object);
public:

	static void _bind_methods();
}

class Nested3 : public Object {
	GDCLASS(Nested3, Object);
public:

	static void _bind_methods();
class Nested4 : public Object {
	GDCLASS(Nested4, Object);
public:

	static void _bind_methods();
}

class Nested1 : public test {
	GDCLASS(Nested1, test);
public:

	static void _bind_methods();
class Nested2 : public Object {
	GDCLASS(Nested2, Object);
public:

	static void _bind_methods();
}

class Nested1 : public test {
	GDCLASS(Nested1, test);
public:

	static void _bind_methods();
class Nested2 : public Object {
	GDCLASS(Nested2, Object);
public:

	static void _bind_methods();
class Nested5 : public Object {
	GDCLASS(Nested5, Object);
public:

	static void _bind_methods();
}

class script_level : public Node {
	GDCLASS(script_level, Node);
public:
	enum  {UNIT_NEUTRAL,UNIT_ENEMY,UNIT_ALLY};
	enum Named {THING_1,THING_2,ANOTHER_THING=-1};

protected:
	Variant export;

	Variant export_param;

	Variant export_flags;

	float get_var3;

public:
	float get_get_var3();

protected:
	float getset_var;

	float DEF =  - 0.1;// comment

public:
	void set_DEF(float value);

	float get_DEF();
	/* signal a() */
	/* signal b(int c, Type* d) */
	void _ready() override;
	void set_export(Variant value);
	Variant get_export();
	void set_export_param(Variant value);
	Variant get_export_param();
	void set_export_flags(Variant value);
	Variant get_export_flags();

	static void _bind_methods();
}

}

#endif // SCRIPT_LEVEL_H
