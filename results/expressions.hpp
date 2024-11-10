
#ifndef EXPRESSIONS_H
#define EXPRESSIONS_H

#include <godot_cpp/godot.hpp>
#include <godot_cpp/variant/array.hpp>
#include <godot_cpp/variant/dictionary.hpp>
#include <godot_cpp/classes/node.hpp>

using namespace godot;

// basic expressions
class expressions : public Node {
	GDCLASS(expressions, Node);
public:

protected:
	Variant foo;
	int orignal;
	static int i;
	const String str = "the fox said \"get off my lawn\"";
	String big_str = "\
	this is a multiline string\
";
	bool _protected_bool = true;
	Array array = Array {/* initializer lists are unsupported */ 0, 1, 2,  };
	bool has_call = array.has(3);
	Dictionary dict = Dictionary {/* initializer lists are unsupported */ {0, 1},{1, 2},{2, 3}, };
	Array string_array = Array {/* initializer lists are unsupported */ "0", "1",  };
	int parenthesis = (42);
	int delayed_expression = 1;
	double asKeyword = 3;
	Array array_of_enum;
	double func_call = Math::sin(34);

// comment \
	double func_delayed = Math::exp(1, 2);

// multi-part expressions
	double arithmetic =  - i * 0.5;
	bool comparison = arithmetic >= 0.5 && arithmetic == 6.0;
	Variant ternary = ( true ? cond_true : cond_false );
	int nested_ternary = ( cond1 && 5 > 6 ? cond1_true * 3 : ( cond2 || (7 < 0) ? cond2_true | 4 : cond12_false && 0 ) );

// hexadecimal
	int byte = (bytes[6] & 0x0f) | 0x40;
};

#endif // EXPRESSIONS_H
