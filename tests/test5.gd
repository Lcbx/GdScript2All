extends Node

func empty(): pass

func reassign():
	reassign += 2

func assign():
	assign = 2


func init(v:= 1.0)->float:
	returning(7.)

func returning(v:float):
	empty()
	return 1.

func declare():
	var declare = 2

func funcception():
	func hi():
		pass