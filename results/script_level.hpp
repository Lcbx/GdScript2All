
#ifndef SCRIPT_LEVEL_H
#define SCRIPT_LEVEL_H

#include <godot_cpp/godot.hpp>

using namespace godot;

namespace godot {

class Nested1 : public test {
	GDCLASS(Nested1, test);
public:

};

class Nested2 : public Object {
	GDCLASS(Nested2, Object);
public:

};

class Nested3 : public Object {
	GDCLASS(Nested3, Object);
public:

};

class Nested4 : public Object {
	GDCLASS(Nested4, Object);
public:

};

class script_level : public Node {
	GDCLASS(script_level, Node);
public:
	enum  {UNIT_NEUTRAL, UNIT_ENEMY, UNIT_ALLY};
	enum Named {THING_1, THING_2, ANOTHER_THING =  - 1};

protected:
	Variant export;

	Variant export_param;

	Variant export_flags;

	double get_var3;

public:
	double get_get_var3();

protected:
	double getset_var;

	double DEF =  - 0.1;// comment

public:
	void set_DEF(double value);

	double get_DEF();
	/* signal a() */
	/* signal b(int c, Ref<Type> d) */

	void _ready() override;
	void set_export(Variant value);
	Variant get_export();
	void set_export_param(Variant value);
	Variant get_export_param();
	void set_export_flags(Variant value);
	Variant get_export_flags();

	static void _bind_methods();
};

VARIANT_ENUM_CAST(script_level::)
VARIANT_ENUM_CAST(script_level::Named)

}

#endif // SCRIPT_LEVEL_H
