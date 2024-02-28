extends Node

class Nested1 extends test:
			
class Nested2:
	class Nested3:

enum {UNIT_NEUTRAL, UNIT_ENEMY, UNIT_ALLY}
enum Named {THING_1, THING_2, ANOTHER_THING = -1}

@export
var export

@export_group("with parameters")

@export(param1, param2)
var export_param

@export_category("category")

@export_flags("Self:4", "Allies:8", "Foes:16")
var export_flags

@export_group("group")
@export_subgroup("subgroup")
@export
var get_var3 :
	get: return get_var3

var getset_var : float : set = _set, get = _get

var DEF = -0.1: # comment
	set(value):
		set_sprite_offset(value)
	get:
		return sprite_offset

signal a()
signal b(c:int,d:Type)
