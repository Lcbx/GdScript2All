
#ifndef EXPRESSIONS_H
#define EXPRESSIONS_H

#include <godot_cpp/godot.hpp>

using namespace godot;

namespace godot {

// basic expressions
class expressions : public Node {
	GDCLASS(expressions, Node);
public:

protected:
	Variant foo;
	static int i = 0;
	const string str = "the fox said \"get off my lawn\"";
	string big_str = "\
	this is a multiline string\
";
	bool _protected_bool = true;
	Array array = new Array{0, 1, 2, };
	Dictionary dict = new Dictionary{{0, 1},{1, 2},{2, 3},};
	Array<string> string_array = new Array{"0", "1", };
	int parenthesis = (42);
	int delayed_expression = 1;
	double asKeyword = 3;

// multi-part expressions
	double arithmetic =  - j * 0.5;
	bool comparison = arithmetic >= 0.5 && arithmetic == 6.0;
	Variant ternary = ( true ? cond_true : cond_false );
	int nested_ternary = ( cond1 && 5 > 6 ? cond1_true * 3 : ( cond2 || (7 < 0) ? cond2_true | 4 : cond12_false && 0 ) );

};

}

#endif // EXPRESSIONS_H
