
#ifndef REFERENCES_H
#define REFERENCES_H

#include <godot_cpp/godot.hpp>
#include <godot_cpp/variant/array.hpp>
#include <godot_cpp/variant/dictionary.hpp>
#include <godot_cpp/classes/node.hpp>

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
};

}

#endif // REFERENCES_H
