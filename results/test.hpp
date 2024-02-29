
#ifndef TEST_H
#define TEST_H

#include <godot_cpp/godot.hpp>

using namespace godot;

namespace godot {

// line comment

/* multiline
   comment
*/

class Nested1 : public test {
	GDCLASS(Nested1, test);
public:

	static void _bind_methods();
}

class test : public Node {
	GDCLASS(test, Node);
public:
	enum  {UNIT_NEUTRAL,UNIT_ENEMY,UNIT_ALLY};
	enum Named {THING_1,THING_2,ANOTHER_THING=-1};

protected:
	Variant export;

	Variant export_param;

	int export_flags;

// basic property definitions / expressions
	Variant foo;
	static int i = 0;
	const string str = "the fox said \"get off my lawn\"";
	string big_str = "\
	this is a multiline string\
";
	Array array = new Array{0,1,2,};
	Dictionary dict = new Dictionary{{0,1},{1,2},{2,3},};
	Array<string> string_array = new Array{"0","1",};

// method

// type inference on members

public:
	float method(float param = 5.0);

protected:
	int j = this->i;
	string k = string_array[0];

// determine type based on godot doc
	Node* x = this->get_parent();
	float x = new Vector3().x;
	Dictionary aClass = ProjectSettings::get_singleton()->get_global_class_list()[10];
	const int flag = RenderingServer::NO_INDEX_ARRAY;
	float global_function = angle_difference(0.1, 0.2);

// Gdscript special syntax
	Node* get_node = get_node("node");
	Node* get_node2 = get_node("../node");
	Node* get_unique_node = get_node("%unique_node");
	Resource* preload_resource = /* preload has no equivalent, add a 'ResourcePreloader' Node in your scene */("res://path");
	Resource* load_resource = load("res://path");

// signals
	/* signal jump() */
	/* signal movement(Vector3 dir, float speed) */

// property getters and setters
	float getset_var;

	float getset_var2 =  - 0.1;

public:
	void set_getset_var2(float value);

	float get_getset_var2();

// this becomes rapidly unreadable once translated though
	void async_function();

protected:
	const Dictionary _default_data = new Dictionary{
	{"t",100},
	{"rafg","asfgh"},
	{"u",false},// Example Comment
	{"r",new Array{"a",new Dictionary{{"b",false},},}},
	{"t",new Dictionary{{"e",new Dictionary{{"g",1},{"f",2},}},}},
	};

// automatic _ready generation
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
}

}

#endif // TEST_H
