#include "methods.hpp"
#include <godot_cpp/core/class_db.hpp>

void methods::empty()
{
}

void methods::reassign()
{
	reassign += 2;
}

void methods::assign()
{
	assign = 2;
}

float methods::init(float v)
{//test2
	//test3
	returning(7.0);
	//test4
}

float methods::returning(float v)
{
	empty();
	return 1.0;
}

void methods::declare()
{
	int declare = 2;
}

float methods::return_inference(float param)
{
	int val = 2;
	return val * param;;static void methods::_bind_methods() {
	ClassDB::bind_method(D_METHOD("empty"), &methods::empty);
	ClassDB::bind_method(D_METHOD("reassign"), &methods::reassign);
	ClassDB::bind_method(D_METHOD("assign"), &methods::assign);
	ClassDB::bind_method(D_METHOD("init", "v"), &methods::init);
	ClassDB::bind_method(D_METHOD("returning", "v"), &methods::returning);
	ClassDB::bind_method(D_METHOD("declare"), &methods::declare);
	ClassDB::bind_method(D_METHOD("return_inference", "param"), &methods::return_inference);

}

}

