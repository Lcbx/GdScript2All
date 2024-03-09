
#ifndef TEST_H
#define TEST_H

#include <godot_cpp/godot.hpp>
#include <godot_cpp/variant/array.hpp>
#include <godot_cpp/variant/dictionary.hpp>
#include <godot_cpp/classes/node.hpp>
#include <godot_cpp/classes/resource.hpp>
#include <godot_cpp/classes/sprite2d.hpp>
#include <godot_cpp/classes/test.hpp>

using namespace godot;

// line comment

/* multiline
   comment
*/

class Nested1 : public test {
	GDCLASS(Nested1, test);
public:

};

class test : public Node {
	GDCLASS(test, Node);
public:
	enum  {UNIT_NEUTRAL, UNIT_ENEMY, UNIT_ALLY};
	enum NamedEnum {THING_1, THING_2, ANOTHER_THING =  - 1};

protected:
	Variant export;

	Variant export_param;

	int export_flags;

// basic property definitions / expressions
	Variant foo;
	static int i;
	const String str = "the fox said \"get off my lawn\"";
	String big_str = "\
	this is a multiline string\
";
	Array array =  /* no array initializer in c++ ! */ {0, 1, 2, };
	Dictionary dict =  /* no dictionary initializer in c++ ! */ {{0, 1},{1, 2},{2, 3},};
	Array string_array =  /* no array initializer in c++ ! */ {"0", "1", };
	Variant complex =  /* no dictionary initializer in c++ ! */ {
		{"t", 100},
		{"rafg", "asfgh"},
		{"u", false},// Example Comment
		{"t",  /* no dictionary initializer in c++ ! */ {{"e",  /* no dictionary initializer in c++ ! */ {{"g", 1},{"f", 2},}},}},
		}["rafg"];

// method

// type inference on members

public:
	double method(double param = 5.0);

protected:
	int j = i;
	String k = string_array[0];

// determine type based on godot doc
	Ref<Node> x = this->get_parent();
	double x = Vector3().x;
	Dictionary aClass = ProjectSettings::get_singleton()->get_global_class_list()[10];
	const ShaderMode enum = RenderingServer::ShaderMode::SHADER_SPATIAL;
	double global_function = Math::angle_difference(0.1, 0.2);

// Gdscript special syntax
	Ref<Node> get_node = get_node("node");
	Ref<Node> get_node2 = get_node("../node");
	Ref<Node> get_unique_node = get_node("%unique_node");
	Ref<Resource> preload_resource = /* preload has no equivalent, add a 'ResourcePreloader' Node in your scene */("res://path");
	Ref<Resource> load_resource = load("res://path");

// getters and setters
	double getset = 0.1;

	Ref<Sprite2D> sprite;

public:
	void set_sprite(Ref<Sprite2D> value);

	Ref<Sprite2D> get_sprite();

// signals
	NamedEnum enumReturn();
	/* signal jump() */
	/* signal movement(Vector3 dir, double speed) */

// _ready generation when @onready is used
	void async_function();

protected:
	int k;

public:
	void _ready() override;
	void set_export(Variant value);
	Variant get_export();
	void set_export_param(Variant value);
	Variant get_export_param();
	void set_export_flags(int value);
	int get_export_flags();

	static void _bind_methods();
};

int test::i = 0;
VARIANT_ENUM_CAST(test::NamedEnum)
VARIANT_ENUM_CAST(test::)

#endif // TEST_H
