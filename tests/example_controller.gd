extends CharacterBody3D
class_name Character

""" 3D character controller
usable for both players and AI
for players, input is handled an overlay script which sets local_dir and view_dir
speed and acceleration is based on movementState which is a Ressource (see MovementState.gd)
"""

# TODO:
# * add ways to get over obstacles
# * implement fall damage
# * hold crouch key to increase gravity ?
# * hold jump key to lower gravity strength ?
# * change gravity into a non-linear acceleration ?

""" movement physics """

const MIN_JUMP_VELOCITY = 3.5
const MAX_Y_SPEED := 10.

const XZ := Vector3(1.,0.,1.) 
const YZ := Vector3(0.,1.,1.) 
const XY := Vector3(1.,1.,0.) 

static var gravity = ProjectSettings.get_setting("physics/3d/default_gravity")

var coyoteTime := Utils.createTimer(self, .15)
var jumpCoolDown := Utils.createTimer(self, .15)


func _process(delta : float):
	# in air
	if not is_on_floor():
		velocity.y = clampf(velocity.y - gravity * delta, -MAX_Y_SPEED, MAX_Y_SPEED)
		movementState = MovementEnum.fall
	else:
		# landing
		if movementState == MovementEnum.fall:
			jumpCoolDown.start()
			# TODO: apply fall damage + play landing animation
		
		# on ground
		movementState = wantedMovement
		coyoteTime.start()
	
	var ground_speed := calculate_ground_speed()

	# jump
	# TODO?: maybe add a special function to jump called on just_pressed
	if global_mov_dir.y > 0. \
		and not coyoteTime.is_stopped() \
		and jumpCoolDown.is_stopped():
		velocity.y += maxf(MIN_JUMP_VELOCITY, ground_speed)
		coyoteTime.stop()
		jump.emit(ground_speed)
	
	# when running, always go forward 
	var direction := global_mov_dir if movementState != MovementEnum.run else basis.z
	
	var top_speed := movements[movementState].top_speed
	var nimbleness := movements[movementState].nimbleness
	var acceleration := movements[movementState].acceleration + ground_speed * nimbleness
	
	var redirect := clampf(1. - nimbleness * delta, 0., 1.)
	var vel_delta := acceleration * delta
	
	velocity.x = move_toward(velocity.x * redirect, direction.x * top_speed, vel_delta)
	velocity.z = move_toward(velocity.z * redirect, direction.z * top_speed, vel_delta)
	
	var new_ground_speed = calculate_ground_speed()
	
	movement.emit(local_dir, new_ground_speed)

	move_and_slide()
	
	for i in range(get_slide_collision_count()):
		collision.emit(get_slide_collision(i))


""" movement state / animations """

signal changedState(state : MovementEnum)
signal collision(collision:KinematicCollision3D)
signal movement(dir:Vector3, speed:float)
signal jump(speed:float)

enum MovementEnum { crouch, walk, run, fall }
@export var movements : Array[MovementState]

var movementState := MovementEnum.walk :
	set(value):
		if movementState != value:
			movementState = value
			changedState.emit(movementState)

var wantedMovement := MovementEnum.walk


""" steering variables """

var _global_mov_dir := Vector3()
var global_mov_dir := Vector3() :
	get: return _global_mov_dir
	set(value):
		_global_mov_dir = value
		# TODO: verify up (y) is not inversed
		_local_dir =  - value * basis.inverse()

# NOTE: local_dir is normalized on the xz plane by Overlay
var _local_dir : Vector3
var local_dir : Vector3 :
	get: return _local_dir
	set(value):
		_local_dir = value
		_global_mov_dir = \
			- value.x * basis.x + \
			value.y * Vector3.UP + \
			value.z * basis.z

func calculate_ground_speed() -> float :
	return sqrt( velocity.x * velocity.x + velocity.z * velocity.z )

""" view """

signal viewDirChanged(euler : Vector3)

var view_dir := Vector3() :
	set(value):
		view_dir = value
		view_dir.x = clampf(view_dir.x, -Globals.view_pitch_limit, Globals.view_pitch_limit)
		viewDirChanged.emit(view_dir)

