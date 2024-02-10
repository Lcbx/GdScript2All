extends Node

class Nested1 extends test:
			
class Nested2:
	class Nested3:

enum {UNIT_NEUTRAL, UNIT_ENEMY, UNIT_ALLY}
enum Named {THING_1, THING_2, ANOTHER_THING = -1}

@export
var export

@export(param1, param2)
var export_param

@export_flags("Self:4", "Allies:8", "Foes:16")
var export_flags

var getset_var : float : set = _set, get = _get

var DEF = -0.1: # Step
	set(value):
		set_sprite_offset(value)
	get:
		return sprite_offset

signal a()
signal b(a:int,b:Type)
