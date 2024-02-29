
#ifndef METHODS_H
#define METHODS_H

// default includes
#include <godot_cpp/godot.hpp>
#include <godot_cpp/core/object.hpp>
#include <godot_cpp/core/class_db.hpp>

using namespace godot;

namespace godot {

class methods : public Node {
	GDCLASS(methods, Node);
public:

	void empty();

	void reassign();

//test1
	void assign();

	float init(float v = 1.0);

	float returning(float v);

	void declare();
	float return_inference(float param = 5.0);

	static void _bind_methods();
}

}

#endif // METHODS_H
