extends Node

# basic expressions
var foo
static var i = 0
const str = 'the fox said "get off my lawn"'
var big_str : string = """
this is a multiline string
"""
var _protected_bool := true
var array = [0,1,2]
var dict := {0:1, 1:2, 2:3}
var string_array : Array[string] = ['0','1']
var parenthesis := (42)
var delayed_expression = \
	1
var asKeyword = 3 as float

# multi-part expressions
var arithmetic = - j * .5
var comparison = arithmetic >= .5 and arithmetic == 6.
var ternary = cond_true if true else cond_false
var nested_ternary = cond1_true * 3 \
	if cond1 and 5 > 6 \
	else cond2_true | 4 \
	if cond2 or (7 < 0) \
	else cond12_false and 0


