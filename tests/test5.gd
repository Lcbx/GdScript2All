extends Node

func empty(): pass

func reassign():
	reassign += 2

func assign():
	assign = 2

#test1
func init(v:= 1.0)->float: #test2
	#test3
	returning(7.)
	#test4

func returning(v:float):
	empty()
	return 1.

func declare():
	var declare = 2