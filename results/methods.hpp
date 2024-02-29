
#ifndef METHODS_H
#define METHODS_H

#include <godot_cpp/godot.hpp>

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
