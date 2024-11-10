
#include "statements.hpp"

#include <godot_cpp/core/object.hpp>
#include <godot_cpp/core/class_db.hpp>
#include <godot_cpp/variant/utility_functions.hpp>

Array statements::method()
{

	int i = 0;

	if(true)
	{
		assert(false);
	}
	else if(false)
	{
		convert("Hello" + " " + "World", TYPE_STRING);
	}
	else if(true)
	{
		UtilityFunctions::print("Goodbye ", "World");
	}
	else
	{
		UtilityFunctions::print(get_stack());
	}

	while(false)
	{
		i += 1;

	// unindented comment
		break;
		continue;
	}

	for(int j=0; j<i; j+=1)
	{
		i += j;
	}

	for(Variant j : array)
	{
		i += j;
	}

	if((bool)dynamic_cast<int*>(&i))
	{i = 0;
	}
	UtilityFunctions::print((bool)dynamic_cast<MeshInstance3D*>(&i));

	switch(i)
	{
		case "1":
		{
			UtilityFunctions::print(i);
			break; }
		case 1:
		{
			UtilityFunctions::print(i);
			break; }
		case 0: if(true)
		{
			UtilityFunctions::print("zero!");

		//var x when false:
			//	print("unreachable")
			//[var x, var y] when true:
			//	print("array pattern")
			//{var x : var y} when true:

			break; }//	print("dictionary pattern")
		default:
		{
			UtilityFunctions::print("unknown");
			break; }
	}

	i += 3 / 3 + 2 * 0.5;

	/* await this->jump; */ // no equivalent to await in c++ !
	/* await this->get_tree()->process_frame; */ // no equivalent to await in c++ !

	get_tree()->emit_signal("process_frame", 0.7);
	get_tree()->connect("process_frame", something);

	return Array();
}

void statements::_bind_methods() {
	ClassDB::bind_method(D_METHOD("method"), &statements::method);

}

