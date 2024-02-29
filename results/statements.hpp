
#ifndef STATEMENTS_H
#define STATEMENTS_H

// default includes
#include <godot_cpp/godot.hpp>
#include <godot_cpp/core/object.hpp>
#include <godot_cpp/core/class_db.hpp>

using namespace godot;

namespace godot {

// method to test statements
class statements : public Node {
	GDCLASS(statements, Node);
public:
	Array method();

	static void _bind_methods();
}

}

#endif // STATEMENTS_H
