@tool
extends Resource
class_name MovementState

## acceleration apllied towward chosen direction
@export var acceleration : float
## redirects a % current velocity toward chosen direction
@export var nimbleness : float
## maximum achievable velocity 
@export var top_speed : float
