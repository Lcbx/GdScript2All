
#ifndef REFERENCES_H
#define REFERENCES_H

// default includes
#include <godot_cpp/godot.hpp>
#include <godot_cpp/core/object.hpp>
#include <godot_cpp/core/class_db.hpp>

using namespace godot;

namespace godot {

class references : public Node {
	GDCLASS(references, Node);
public:

protected:
	Variant variable = foo;
	Variant reference = foo.bar;
	Variant function = foo();
	Variant functionParams = foo(a, b);
	Variant method = foo.bar();
	Variant functionMethodParams = foo(a, b).bar(c, d);
	Variant refMethod = foo.bar.baz();
	Variant methodRef = foo.bar().baz;
	Variant subscription = this->dict[0];
public:

	static void _bind_methods();
}

}

#endif // REFERENCES_H
