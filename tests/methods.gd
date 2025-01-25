extends Node

func empty(): pass

func reassign():
	reassign += 2

func assign() -> void:
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
	
func return_inference(param = 5.):
	var val = 2
	return val * param