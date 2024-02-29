
#include "statements.hpp"
#include <godot_cpp/core/object.hpp>
#include <godot_cpp/core/class_db.hpp>

Array statements::method()
{
	
			int i = 0;
	
	if(ABC)
	{
		assert(false);
	}
	else if(false)
	{
		print("Hello" + " " + "World");
	}
	else if(true)
	{
		print("Goodbye ", "World");
	}
	else
	{
		print(i);
	}
	
	while(false)
	{
		i += 1;
		break;
		continue;
	}
	
	for(int j : range(i))
	{
		i += j;
	}
	
	switch(i)
	{
		case "1":
		{
			print(i);
			break;
		}
		case 1:
		{
			print(i);
			break;
		}
		case 0: if(true)
		{
			print("zero!");
			break;
		}
		//var x when false:
		//	print("unreachable")
		//[var x, var y] when true:
		//	print("array pattern")
		//{var x : var y} when true:
		//	print("dictionary pattern")
		default:
		{
			print("unknown");
			break;
		}
	}
	
	i += 3 / 3 + 2 * 0.5;
	
	/* await self.jump; */ // no equivalent to await in c++ !
	/* await self.get_tree()->process_frame; */ // no equivalent to await in c++ !
	
	get_tree()->emit_signal("process_frame", 0.7);
	get_tree()->connect("process_frame", something);
	
	return new Array{};;static void statements::_bind_methods() {
	ClassDB::bind_method(D_METHOD("method"), &statements::method);

}

}

