from StringBuilder import StringBuilder
from godot_types import godot_types


class Transpiler:
	
	def __init__(self, vprint):
		
		# verbose printing
		self.vprint = vprint
		
		# scope level
		self.level = 0
		
		# script level class name
		self.script_class = ''
		
		# onready assignments
		# they are moved moved to the ready function of the corresponding class
		# (class_name:assignment_str)
		self.onready_assigns = {}
		
		# annotations (property_name:tuple<annotation_name,params> )
		self.annotations = {}
		
		# header definitions (class_name:Stringbuilder)
		# NOTE: cpp actually supports nested classes
		# but it is frowned upon, so we flatten them
		self.hpps = {}
		
		# for cpp, we use layers only in .cpp
		self.layers = [StringBuilder()]
		
		# result hpp
		self.hpp = ''
		# result cpp
		self.cpp = ''
		
	
	# class name as str and class definition as ClassData
	def current_class(self, class_name, klass):
		self.class_name = class_name
		self.klass = klass
		# first defined class is script-level class
		if not self.script_class: self.script_class = class_name
	
	def define_class(self, name, base_class, is_tool):
		self.hpps[name] = StringBuilder()
		self.getHpp() + f'''
class {name} : public {base_class} {{
	GDCLASS({name}, {base_class});
protected:
	static void _bind_methods();
public:
'''
	
	def getHpp(self):
		return self.hpps[self.class_name]
	
	# NOTE: enums have similar syntax in gdscript, C# and cpp
	# lazily passing the enum definition as-is for now
	def enum(self, name, definition):
		self.getHpp() + f'\tenum {name} {definition}\n'
	
	def annotation(self, name, params, memberName):
		# TODO: add corresponding bindings in _bind_methods()
		self.annotations[memberName] = (name, params)
	
	def declare_property(self, type, name, constant, static):
		type = translate_type(type)
		const_decl = 'const ' if constant else 'static ' if static else ''
		exposed = 'protected' if name[0] == '_' else 'public'
		self += f'{exposed} {const_decl}{type} {name}'
	
	def setget(self, member, accessors):
		self.addLayer()
		self.UpScope()
		self += '\n'
		last_accessor = None
		
		# call the appropriate Transpiler method (defined afterward)
		for accessor in accessors:
			method_name = accessor[0]
			method = getattr(self,method_name)
			params = accessor[1:]
			method(member, *params)
			last_accessor = method_name
		
		# add mssing bracket when using a method as last accesor
		if 'method' in last_accessor:
			self.level -= 1;
			self += '\n}'
		# otherwise an extra downscope was done already
		
		code = self.popLayer()
		
		# add private property if missing
		if not toPrivate(member) in self.klass.members:
			privateMember = '}\n' + '\t' * self.level + \
				f'private {self.klass.members[member]} {toPrivate(member)};\n'
			code = rReplace(code, '}', privateMember)
		
		# this is for prettiness
		code = code.replace('\t' * (self.level+1) + '\n', '')
		self.write(code)
		
		
	def getter_method(self, member, getterName):
		self += f'get => {getterName}();\n'
	
	def setter_method(self, member, setterName):
		self += f'set => {setterName}(value);\n'
	
	def getter(self, member, code):
		self += 'get';
		code = self.cleanGetSetCode(code, member)
		self.write(code)
	
	def setter(self, member, valueName, code):
		self += 'set';
		code = self.cleanGetSetCode(code, member)
		self.write(code.replace(valueName, 'value'))
	
	def cleanGetSetCode(self, code, member):
		# use private value
		if not toPrivate(member) in self.klass.members:
			code = code.replace(member, toPrivate(member))
		return code

	
	def declare_variable(self, type, name):
		self += f'var {name}'
	
	def define_method(self, name, params = {}, params_init = {}, return_type = None, code = '', static = False):
		return_type = translate_type(return_type)
		
		if not code:
			self.addLayer(); self += '\n{\n}'; code = self.popLayer()
		
		exposed = 'protected' if name[0] == '_' else 'public'
		static_str = 'static ' if static else ''
		self += f'{exposed} {static_str}{return_type} {name}('
		
		for i, (pName, pType) in enumerate(params.items()):
			if i != 0: self += ', '
			self += f'{translate_type(pType)} {pName}'
			if pName in params_init:
				self += ' = '; get(params_init[pName])
		
		self += ')'
		
		# add onready assignments if method is _ready
		if name == '_ready' and self.class_name in self.onready_assigns:
			onreadies = self.onready_assigns[self.class_name]
			tabs = '\t' * (self.level +1)
			onreadies_code = '{' + ''.join(map(lambda stmt: f'\n{tabs}{stmt};', onreadies))
			code = code.replace('{', onreadies_code, 1)
			del self.onready_assigns[self.class_name]
					
		self.write(code)
	
	def define_signal(self, name, params):
		paramStr = ','.join( ( f'{translate_type(pType)} {pName}' for pName, pType in params.items()))
		self += '[Signal]\n'
		self += f'public delegate void {name}Handler({paramStr});'
	
	def assignment(self, exp, onreadyName):
		if onreadyName:
			self.addLayer()
			self.write(f'{onreadyName} = '); get(exp)
			self.onready_assigns.setdefault(self.class_name, []).append(self.popLayer())
			return
		self += ' = '; get(exp)
	
	def subexpression(self, expression):
		self += '('; get(expression); self += ')'
	
	def create_array(self, values):
		self += 'new Array{'; self.level += 1
		for value in values:
			get(value); self += ','
		self += '}'; self.level -= 1
		
	def create_dict(self, kv):
		self += 'new Dictionary{'; self.level += 1
		for key, value in kv:
			self += '{'; get(key); self += ','; get(value); self+= '},'
		self += '}'; self.level -= 1
	
	def create_dict(self, kv):
		self += 'new Dictionary{'; self.level += 1
		for key, value in kv:
			self += '{'; get(key); self += ','; get(value); self+= '},'
		self += '}'; self.level -= 1
	
	def create_lambda(self, params, code):
		self += '('
		for i, (pName, pType) in enumerate(params.items()):
			if i != 0: self += ', '
			self += f'{translate_type(pType)} {pName}'
		self += ') =>'
		# cleanup
		code = code.replace('{', '{\t', 1)
		code = code.replace(';;', ';')
		code = rReplace(code, '}', '};')
		self.write(code)
	
	def literal(self, value):
		# strings
		if isinstance(value, str):
			# add quotes / escape the quotes inside if necessary
			if '\n' in value: value = f'@"{value}"'
			else:
				value = value.replace('"', '\\"')
				value = f'"{value}"'
		
		# booleans
		elif isinstance(value, bool):
			self += str(value).lower(); return
		
		self += str(value)
	
	def constant(self, name):
		# Note: in c++ this would be ::<name>
		self += '.' + name
	
	def this(self):
		self += 'this.'
	
	def property(self, name):
		self += name
	
	def variable(self, name):
		#TODO: update replacements for cpp
		self += variable_replacements.get(name, None) or name
	
	def singleton(self, name):
		self += translate_type(name)
	
	def reference(self, name):
		self += '.' + name
	
	def call(self, name, params, global_function = False):
		if global_function: name = function_replacements.get(name, name)
		self += name + '('
		for i, p in enumerate(params):
			if i>0: self += ', '
			get(p)
		self += ')'
	
	def constructor(self, name, params):
		self += 'new '; self.call(name, params)
	
	def subscription(self, key):
		self+= '['; get(key); self += ']'
		
	def operator(self, op):
		op = '&&' if op == 'and' \
			else '||' if op == 'or' \
			else '!' if op == 'not' \
			else op
		if op == '!': self += op
		else: self += f' {op} '
	
	def ternary(self, iterator):
		# condition, valueIfTrue, valueIfFalse
		self += '( '
		get(iterator); self += ' ? ';
		get(iterator); self += ' : '; get(iterator);
		self += ' )'
	
	def returnStmt(self, return_exp):
		self += 'return '; get(return_exp)
	
	def ifStmt(self, condition):
		self += 'if('; get(condition); self += ')'
	
	def elifStmt(self, condition):
		self += 'else if('; get(condition); self += ')'
	
	def elseStmt(self):
		self += 'else'
	
	def whileStmt(self, condition):
		self += 'while('; get(condition); self += ')'
		
	def forStmt(self, name, type, exp):
		self += f'foreach({type} {name} in '; get(exp); self += ')'
	
	def breakStmt(self): self += 'break;'
	
	def continueStmt(self): self += 'continue;'
	
	def awaitStmt(self, object, signalName):
		object = 'this' if object == 'self' else object
		self += f'await ToSignal({object}, "{signalName}");'
	
	def emitSignal(self, name, params):
		self += f'EmitSignal("{name}"'
		for i, p in enumerate(params):
			self += ', '
			get(p)
		self += ')'
	
	def connectSignal(self, name, params):
		self += f'{name} += '; get(params[0])
	
	def matchStmt(self, evaluated, cases):
		
		type = get(evaluated)
		
		# use switch on literals
		if type in ('int', 'string', 'float'):
			
			self += 'switch('; get(evaluated); self += ')'
			self.UpScope()
			
			for pattern, when in cases(True):
				if pattern == 'default':
					self += 'default:'
				else:
					self += 'case '; get(pattern); self += ':'
					if when: self += ' if('; get(when); self += ')'
		
		 # default to if else chains for objects
		else:
			self.addLayer()
			self += 'if('
			get(evaluated)
			self += ' == '
			comparison = self.popLayer()
			
			for pattern, when in cases():
				if pattern == 'default':
					self += 'else '
				else:
					self.write(comparison)
					get(pattern)
					if when: self += ' && '; get(when)
					self += ')'
	
	def end_class(self, name):
		# add ready function if there are onready_assigns remaining
		# NOTE : we can end up with 2 _ready functions in generated code
		# we could fix this by accumulating onreadies (and _ready definition if exists)
		# then appending it at the end on script
		# (or replacing a dummy string ex:__READY__ if _ready was defined by user)
		if name in self.onready_assigns:
			self.define_method('_ready')
		
		# TODO: add bindings
	
	def end_script(self):
		self.end_class(self.script_class)
		
		# close remaining scopes (notably script-level class)
		while len(self.layers) > 1: self.write(self.popLayer())
		while self.level > 0: self.DownScope()
		
		# NOTE: this is not necessarily the name of the hpp file !
		self.cpp = f'#include "{self.class_name}".hpp"\n\n' + self.getLayer().getvalue()
		
		hpp = StringBuilder()
		for sb in self.hpps.values(): hpp += sb.getvalue()
		self.hpp = '''
#ifndef __CLASS___H
#define __CLASS___H

#include <Godot.hpp>

using namespace godot;

__IMPLEMENTATION__

#endif // __CLASS___H
'''.replace('__CLASS__', self.script_class.upper()).replace('__IMPLEMENTATION__', hpp.getvalue())
	
	def comment(self, content):
		self += f"//{content}"
	
	def multiline_comment(self, content):
		self += f"/*{content}*/"
	
	def end_statement(self):
		self += ';'
	
	""" code generation utils """
	
	# += operator override to generate code
	def __iadd__(self, txt):
		# automatic indentation
		if '\n' in txt: txt = txt.replace('\n', '\n' + '\t' * self.level)
		self.write(txt)
		self.vprint(">", txt.replace("\n", "<EOL>").replace('\t', '  '))
		return self
	
	def write(self, txt):
		self.getLayer().write(txt)
	
	def get_result(self):
		return (self.hpp, self.cpp)
	
	def save_result(self, outname):
		if not outname.endswith('.cpp'): outname += '.cpp'
		
		result = self.get_result()
		
		with open(outname.replace('.cpp', '.hpp'),'w+') as wf:
			wf.write(result[0])
			
		with open(outname,'w+') as wf:
			wf.write(result[1])
	
	def UpScope(self):
		self.vprint('UpScope')
		self += '\n{'
		self.level += 1
	
	def DownScope(self):
		self.vprint('DownScope')
		self.level -= 1
		self += '\n}'
	
	# layers : used for method definition
	# so we can parse return type then add code
	
	def getLayer(self):
		return self.layers[-1]
	
	def addLayer(self):
		self.layers.append(StringBuilder())
		
	def popLayer(self):
		# add top scope txt to lower then remove top
		scope = self.layers[-1].getvalue()
		self.layers.pop()
		return scope

def rReplace(string, toReplace, newValue, n = 1):
	return newValue.join(string.rsplit(toReplace,n))

def toPrivate(name):
	return '_' + name

def translate_type(type):
	if type == None: return 'void'
	if type in ['Array', 'Dictionary']: return type
	if type in godot_types: return f'Godot.{type}'
	if type.endswith('[]'): return f'Array<{type[:-2]}>'
	if type == 'float': return 'double' # C# uses doubles
	return type

# trick for generator values
get = next

export_replacements = {
	"export_range":"Export(PropertyHint.Range,",
	"export_exp_easing ": "Export(PropertyHint.ExpEasing)",
	"export_color_no_alpha":"Export(PropertyHint.ColorNoAlpha)",
	"export_flags":"Export(PropertyHint.Flags,",
	"export_enum":"Export(PropertyHint.Enum,",
	# TODO: fill more if needed /possible
}

variable_replacements = {
	"self":"this",
	"PI":"Mathf.Pi",
	"TAU":"Mathf.Tau",
	"INF":"Mathf.Inf",
	"NAN":"Mathf.NaN",
	"TYPE_ARRAY":"typeof(Array)",
	"TYPE_BOOL":"typeof(bool)",
	"TYPE_COLOR":"typeof(Color)",
	"TYPE_DICTIONARY":"typeof(Dictionary)",
	"TYPE_INT":"typeof(int)",
	"TYPE_NIL":"null",
	"TYPE_OBJECT":"typeof(Godot.Object)",
	"TYPE_REAL":"typeof(double)",
	"TYPE_RECT2":"typeof(Rect2)",
	"TYPE_RID":"typeof(RID)",
	"TYPE_STRING":"typeof(string)",
	"TYPE_VECTOR2":"typeof(Vector2)",
}

function_replacements = {
	'preload': "/* preload has no equivalent, add a 'ResourcePreloader' Node in your scene */",
	'weakref': 'GodotObject.WeakRef(obj)',
	'instance_from_id' : 'GodotObject.InstanceFromId',
	'is_instance_id_valid' : 'GodotObject.IsInstanceIdValid',
	'is_instance_valid' : 'GodotObject.IsInstanceValid',
	'abs' : 'Mathf.Abs',
	'absf' : 'Mathf.Abs',
	'absi' : 'Mathf.Abs',
	'acos' : 'Mathf.Acos',
	'acosh' : 'Mathf.Acosh',
	'angle_difference' : 'Mathf.AngleDifference',
	'asin' : 'Mathf.Asin',
	'asinh' : 'Mathf.Asinh',
	'atan' : 'Mathf.Atan',
	'atan2' : 'Mathf.Atan2',
	'atanh' : 'Mathf.Atanh',
	'bezier_derivative' : 'Mathf.BezierDerivative',
	'bezier_interpolate' : 'Mathf.BezierInterpolate',
	'bytes_to_var' : 'GD.BytesToVar',
	'bytes_to_var_with_objects' : 'GD.BytesToVarWithObjects',
	'ceil' : 'Mathf.Ceil',
	'ceilf' : 'Mathf.Ceil',
	'ceili' : 'Mathf.CeilToInt',
	'clamp' : 'Mathf.Clamp',
	'clampf' : 'Mathf.Clamp',
	'clampi' : 'Mathf.Clamp',
	'cos' : 'Mathf.Cos',
	'cosh' : 'Mathf.Cosh',
	'cubic_interpolate' : 'Mathf.CubicInterpolate',
	'cubic_interpolate_angle' : 'Mathf.CubicInterpolateAngle',
	'cubic_interpolate_angle_in_time' : 'Mathf.CubicInterpolateInTime',
	'cubic_interpolate_in_time' : 'Mathf.CubicInterpolateAngleInTime',
	'db_to_linear' : 'Mathf.DbToLinear',
	'deg_to_rad' : 'Mathf.DegToRad',
	'ease' : 'Mathf.Ease',
	'error_string' : 'Error.ToString',
	'exp' : 'Mathf.Exp',
	'floor' : 'Mathf.Floor',
	'floorf' : 'Mathf.Floor',
	'floori' : 'Mathf.FloorToInt',
	'fmod' : '/* no equivalent function, use operator % */',
	'fposmod' : 'Mathf.PosMod',
	'hash' : 'GD.Hash',
	'instance_from_id' : 'GodotObject.InstanceFromId',
	'inverse_lerp' : 'Mathf.InverseLerp',
	'is_equal_approx' : 'Mathf.IsEqualApprox',
	'is_finite' : 'Mathf.IsFinite',
	'is_inf' : 'Mathf.IsInf',
	'is_instance_id_valid' : 'GodotObject.IsInstanceIdValid',
	'is_instance_valid' : 'GodotObject.IsInstanceValid',
	'is_nan' : 'double.IsNaN',
	'is_same' : 'ReferenceEquals',
	'is_zero_approx' : 'Mathf.IsZeroApprox',
	'lerp' : 'Mathf.Lerp',
	'lerp_angle' : 'Mathf.LerpAngle',
	'lerpf' : 'Mathf.Lerp',
	'linear_to_db' : 'Mathf.LinearToDb',
	'log' : 'Mathf.Log',
	'max' : 'Mathf.Max',
	'maxf' : 'Mathf.Max',
	'maxi' : 'Mathf.Max',
	'min' : 'Mathf.Min',
	'minf' : 'Mathf.Min',
	'mini' : 'Mathf.Min',
	'move_toward' : 'Mathf.MoveToward',
	'nearest_po2' : 'Mathf.NearestPo2',
	'pingpong' : 'Mathf.PingPong',
	'posmod' : 'Mathf.PosMod',
	'pow' : 'Mathf.Pow',
	'print' : 'GD.Print',
	'print_rich' : 'GD.PrintRich',
	'printerr' : 'GD.PrintErr',
	'printraw' : 'GD.PrintRaw',
	'prints' : 'GD.PrintS',
	'printt' : 'GD.PrintT',
	'push_error' : 'GD.PushError',
	'push_warning' : 'GD.PushWarning',
	'rad_to_deg' : 'Mathf.RadToDeg',
	'rand_from_seed' : 'GD.RandFromSeed',
	'randf' : 'GD.Randf',
	'randf_range' : 'GD.RandRange',
	'randfn' : 'GD.Randfn',
	'randi' : 'GD.Randi',
	'randi_range' : 'GD.RandRange',
	'randomize' : 'GD.Randomize',
	'remap' : 'Mathf.Remap',
	'rotate_toward' : 'Mathf.RotateToward',
	'round' : 'Mathf.Round',
	'roundf' : 'Mathf.Round',
	'roundi' : 'Mathf.RoundToInt',
	'seed' : 'GD.Seed',
	'sign' : 'Mathf.Sign',
	'signf' : 'Mathf.Sign',
	'signi' : 'Mathf.Sign',
	'sin' : 'Mathf.Sin',
	'sinh' : 'Mathf.Sinh',
	'smoothstep' : 'Mathf.SmoothStep',
	'snapped' : 'Mathf.Snapped',
	'snappedf' : 'Mathf.Snapped',
	'snappedi' : 'Mathf.Snapped',
	'sqrt' : 'Mathf.Sqrt',
	'step_decimals' : 'Mathf.StepDecimals',
	'str_to_var' : 'GD.StrToVar',
	'tan' : 'Mathf.Tan',
	'tanh' : 'Mathf.Tanh',
	'type_convert' : 'GD.Convert',
	'type_string' : 'Variant.Type.ToString',
	'typeof' : 'Variant.VariantType',
	'var_to_bytes' : 'GD.VarToBytes',
	'var_to_bytes_with_objects' : 'GD.VarToBytesWithObjects',
	'var_to_str' : 'GD.VarToStr',
	'weakref' : 'GodotObject.WeakRef',
	'wrap' : 'Mathf.Wrap',
	'wrapf' : 'Mathf.Wrap',
	'wrapi' : 'Mathf.Wrap'
}