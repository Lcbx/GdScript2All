
#ifndef METHODS_H
#define METHODS_H

#include <godot_cpp/godot.hpp>
#include <godot_cpp/variant/array.hpp>
#include <godot_cpp/variant/dictionary.hpp>
#include <godot_cpp/classes/node.hpp>

using namespace godot;

class methods : public Node {
	GDCLASS(methods, Node);
public:

	void empty();

	void reassign();

//test1
	void assign();

	double init(double v = 1.0);

	double returning(double v);

	void declare();

	double return_inference(double param = 5.0);

	static void _bind_methods();
};

#endif // METHODS_H
