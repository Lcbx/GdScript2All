from re import sub as regex_replace
from godot_types import *

from StringBuilder import StringBuilder

class Transpiler:
	
	def __init__(self, script_name, out_name, vprint):
		
		self.out_name = out_name
		
		# verbose printing
		self.vprint = vprint
		
		# scope level
		self.level = 0
		
		# onready assignments
		# they are moved moved to the ready function of the corresponding class
		# (class_name:assignment_str)
		self.onready_assigns = {}
		
		# unnamed enums don't exist in C#, so we use a counter to give them a name
		self.unnamed_enums = 0
		
		# allows to parse code and rearrange it
		self.layers = [StringBuilder()]
		
		# result cs
		self.cs = ''
	
	# ClassData (methods and member types, generated by parser)
	# NOTE: helps since classes can be nested
	def current_class(self, class_name, klass):
		self.class_name = class_name
		self.klass = klass
	
	def define_class(self, name, base_class, is_tool, is_main):
		if is_tool: self += '[Tool]\n'

		# automatically registers Resource-derived classes
		# allows interop with Gdscript
		# I think this should be standard behaviour tbh
		if is_main: self += '[GlobalClass]\n'
		
		self += f'public partial class {name} : {translate_type(base_class)}'
		self.UpScope()
		self += '\n'
	
	def enum(self, name, params, params_init):
		def_ = ''
		for i, (pName, pType) in enumerate(params.items()):
				if i != 0: def_ += ', '
				def_ += pName
				if pName in params_init:
					self.addLayer(); get(params_init[pName])
					def_ += ' = ' + self.popLayer()
		# unnamed enums not supported in C#
		if not name: name  = f'Enum{self.unnamed_enums}'; self.unnamed_enums += 1
		self += f'public enum {name} {{{def_}}}'
	
	# NOTE: endline is the following space, for prettier output
	def annotation(self, name, params, memberName, endline):
		# https://docs.godotengine.org/en/stable/tutorials/scripting/gdscript/gdscript_exports.html
		# https://docs.godotengine.org/en/stable/tutorials/scripting/c_sharp/c_sharp_exports.html
		replaced = name in export_replacements
		start = export_replacements[name] if replaced else toPascal(name) + (params and '(')
		if replaced and params: start += ', '
		self += f'[{start}"{params}")]' if params else f'[{start}]'
		self.write(endline if endline else ' ')
	
	def declare_property(self, type, name, assignment, accessors, constant, static, onready):
		pascalName = toPascal(name)
		const_decl = 'const ' if constant else 'static ' if static else ''
		exposed = 'protected' if name[0] == '_' else 'public'
		self += f'{exposed} {const_decl}{translate_type(type)} {pascalName}'

		assignment_str = ''
		if assignment:
			self.addLayer(); self.assignment(assignment)
			assignment_str = self.popLayer() 

			if onready:
				self.onready_assigns.setdefault(self.class_name, []) \
					.append(pascalName + assignment_str)
			elif accessors: pass
			else: self.write(assignment_str)

		# setget
		if accessors:
			self.addLayer()

			self.UpScope()
			self += '\n'

			set_defined = False
			get_defined = False
			last_accessor = None

			for accessor in accessors:
				method_name = accessor[0]
				set_defined = set_defined or method_name.startswith('set')
				get_defined = get_defined or method_name.startswith('get')
				method = getattr(self,method_name)
				params = accessor[1:]
				method(name, *params)
				last_accessor = method_name
			
			# add mssing bracket when using a method as last accesor
			if 'method' in last_accessor:
				self.level -= 1;
				self += '\n}'
			# otherwise an extra downscope was done already
			
			code = self.popLayer()
			
			# add private property if missing)
			private_version = toPrivate(name)
			if not private_version in self.klass.members:
				privateMember = '}\n' + '\t' * self.level + \
					f'private {translate_type(type)} {toPascal(private_version)}'
				if assignment_str: privateMember += assignment_str
				privateMember += ';\n'
				code = replaceClosingBrace(code, privateMember)

			# add missing getters / setters
			if not set_defined or not get_defined:
				self.addLayer()
				if set_defined:
					self.getter(name, f' {{ return {pascalName}; }}'); self += '\n'
				else:
					self.setter(name, 'value', f' {{ {pascalName} = value; }}'); self += '\n'
				code = replaceClosingBrace(code, f'\t{self.popLayer()}}}')

			self.write(code)
		
		
	def getter_method(self, member, getterName):
		getterName = toPascal(getterName)
		self += f'get => {getterName}();\n'
	
	def setter_method(self, member, setterName):
		setterName = toPascal(setterName)
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
		# use private value instead of property name
		if not toPrivate(member) in self.klass.members:
			# using capture groups to keep non-word characters (that delimit name)
			code = regex_replace(fr'(\W){toPascal(member)}(\W)', fr'\1{toPrivate(toPascal(member))}\2', code)
		return code
	
	def declare_variable(self, type, name, assignment):
		self += f'var {name}'
		if assignment: self += ' = '; get(assignment)
	
	def define_method(self, name, params = {}, params_init = {}, return_type = None, code = '', static = False, override = False):
		
		if not code:
			self.addLayer(); self += '\n{\n}'; code = self.popLayer()
		
		exposed = 'protected' if name[0] == '_' and not override else 'public'
		static_str = 'static ' if static else ''
		override_str = 'override ' if override else ''
		self += f'{exposed} {override_str}{static_str}{translate_type(return_type)} {toPascal(name)}('
		
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
		paramStr = ', '.join( ( f'{translate_type(pType)} {pName}' for pName, pType in params.items()))
		self += '[Signal]\n'
		self += f'public delegate void {toPascal(name)}EventHandler({paramStr});'
	
	def assignment(self, exp):
		self += ' = '; get(exp)
	
	def subexpression(self, expression):
		self += '('; get(expression); self += ')'
	
	def create_array(self, values):
		self += 'new Array{'
		self += values
		self += '}'

	def array_item(self, item):
		get(item); self += ', '
		
	def create_dict(self, values):
		self += 'new Dictionary{'
		self += values
		self += '}'

	def dict_item(self, key, value):
		self += '{'; get(key); self += ', '; get(value); self += '},'
	
	def create_lambda(self, params, code):
		self += '('
		for i, (pName, pType) in enumerate(params.items()):
			if i != 0: self += ', '
			self += f'{translate_type(pType)} {pName}'
		self += ') =>'
		# cleanup
		code = code.replace('{', '{\t', 1)
		code = replaceClosingBrace(code, '};')
		self.write(code)
	
	def literal(self, value):
		if isinstance(value, str):
			# add quotes / escape the quotes inside if necessary
			if '\n' in value: value = f'@"{value}"'
			else:
				value = value.replace('"', '\\"')
				value = f'"{value}"'

		elif isinstance(value, bool):
			value = str(value).lower()
		
		self.write(str(value))
	
	def constant(self, name):
		self += '.' + (name if not name.isupper() else toPascal(name.lower()) )
	
	def property(self, name):
		self += toPascal(name)
	
	def variable(self, name):
		self += variable_replacements.get(name, name)
	
	def singleton(self, name):
		self += translate_type(name)
	
	def reference(self, name, obj_type, member_type, is_singleton = False):
		self += '.' + toPascal(name)

	def reassignment(self, name, obj_type, member_type, is_singleton, op, val):
		self += f'.{toPascal(name)} {op} '; get(val)
	
	def call(self, calling_type, name, params):
		if calling_type == GLOBALS: name = function_replacements.get(name, name)
		
		# for some reason, API diverges here
		elif name == 'has':
			name = ('Contains' if calling_type == 'Array'
				else 'ContainsKey' if calling_type == 'Dictionary'
				else name )

		self += toPascal(name) + '('
		for i, p in enumerate(params):
			if i>0: self += ', '
			get(p)
		self += ')'
	
	def constructor(self, name, type, params):
		self += 'new '; self.call(type, name, params)
	
	def subscription(self, key):
		self+= '['; get(key); self += ']'
		
	def operator(self, op):
		op = '&&' if op == 'and' \
			else '||' if op == 'or' \
			else '!' if op == 'not' \
			else op
		if op == '!': self += op
		else: self += f' {op} '
	
	def check_type(self, exp, checked):
		get(exp); self += f' is {translate_type(checked)}'

	def ternary(self, condition, valueIfTrue, valueIfFalse):
		self += '( '
		get(condition); self += ' ? '; get(valueIfTrue); self += ' : '; get(valueIfFalse);
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
		self += f'await ToSignal({object}, "{toPascal(signalName)}");'
	
	def emitSignal(self, signalName, params):
		self += f'EmitSignal("{toPascal(signalName)}"'
		for i, p in enumerate(params):
			self += ', '
			get(p)
		self += ')'
	
	def connectSignal(self, signalName, params):
		self += f'{toPascal(signalName)} += '; get(params[0])
	
	def matchStmt(self, evaluated, cases):
		type = get(evaluated)
		
		# use switch on literals
		if type in ('int', 'string', 'float'):
			
			self += 'switch('; get(evaluated); self += ')'
			self.UpScope()
			
			for pattern, when, code in cases():
				if pattern == 'default':
					self += 'default:'
				else:
					self += 'case '; get(pattern); self += ':'
					if when: self += ' if('; get(when); self += ')'
				code = replaceClosingBrace(code, '\tbreak; }')
				self.write(code)
		
		 # default to if else chains for objects
		else:
			self.addLayer()
			self += 'if('
			get(evaluated)
			self += ' == '
			comparison = self.popLayer()
			
			for pattern, when, code in cases():
				if pattern == 'default':
					self += 'else '
				else:
					self.write(comparison)
					get(pattern)
					if when: self += ' && '; get(when)
					self += ')'
				self.write(code)
	
	def end_class(self, name):
		# add ready function if there are onready_assigns remaining
		# NOTE : we can end up with 2 _ready functions in generated code
		# we could fix this by accumulating onreadies (and _ready definition if exists)
		# then appending it at the end on script
		# (or replacing a dummy string ex:__READY__ if _ready was defined by user)
		if name in self.onready_assigns:
			self.define_method('_ready', override=True)
	
	def end_script(self):
		self.end_class(self.class_name)
		
		# close remaining scopes (notably script-level class)
		while len(self.layers) > 1: self.write(self.popLayer())
		while self.level > 0: self.DownScope()
		
		self.cs = header + prettify(str(self.getLayer()))
	
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
		self.vprint("emit:", txt.replace("\n", "<EOL>").replace('\t', '  '))
		return self
	
	def write(self, txt):
		self.getLayer().write(txt)
	
	def get_result(self):
		return (self.cs,) 
	
	def save_result(self):
		if not self.out_name.endswith('.cs'): self.out_name += '.cs'
		with open(self.out_name,'w+') as wf:
			wf.write(self.get_result()[0])
	
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
		scope = str(self.layers[-1])
		self.layers.pop()
		return scope

def translate_type(type):
	if type == None: return 'void'
	if type.endswith('[]'): return f'Array<{type[:-2]}>'
	if type.endswith('enum'): return type[:-len('enum')]
	if type == 'float' and not use_floats: return 'double'
	if isVariantType(type): return type
	if type.split('.') [-1] in godot_types: return f'Godot.{type}'
	return type

def rReplace(string, toReplace, newValue, n = 1): return newValue.join(string.rsplit(toReplace,n))

def replaceClosingBrace(string, replacement):
	def impl():
		open_brackets = 0
		for c in string:
			if c == '{': open_brackets += 1
			elif c == '}':
				open_brackets -= 1
				if open_brackets == 0:
					yield replacement
					# ensure it triggers only once
					open_brackets = 999
					continue
			yield c
	return ''.join(impl())

def toPrivate(name): return '_' + name

def toPascal(text):
	split_ = text.split('_')
	
	# for legible contants
	if all(map(lambda s: s.isupper(), split_)): return text
	
	# keep start underscores _
	nStart_ = next( (i for i, c in enumerate(text) if c != '_'), 0)
	
	capitalize = lambda s: s[0].upper() + s[1:] if s else s
	return  '_' * nStart_ + ''.join( map(capitalize, split_ ) )

def isVariantType(type):
	match = (vt for vt in variant_types if vt.replace('TYPE_', '', 1).replace('_','') == type.upper() if type != 'Object')
	return next(match, None) != None

# for prettier output
def prettify(value):
	def impl():
		cnt = 0
		line = ''
		for c in value:
			if c == '\n':
				line = ''
				cnt += 1
				if cnt < 4: yield c
			elif cnt > 0 and c == ';':  pass
			elif cnt > 0 and c == ' ':  line += c
			elif cnt > 0 and c == '\t': line += c
			else: cnt = 0; yield line + c; line = ''
	return ''.join(impl())

# trick for generator values
get = next

# Default imports and aliases that almost every class needs.
header = """using Godot;
using Godot.Collections;"""
# we don't need System afaik
#using System;\n'
#using Array = Godot.Collections.Array;
#using Dictionary = Godot.Collections.Dictionary;

export_replacements = {
	'export_range':'Export(PropertyHint.Range',
	'export_enum':'Export(PropertyHint.Enum',
	'export_enum_suggestion':'Export(PropertyHint.EnumSuggestion',
	'export_exp_easing':'Export(PropertyHint.ExpEasing',
	'export_link':'Export(PropertyHint.Link',
	'export_flags':'Export(PropertyHint.Flags',
	'export_layers_2d_render':'Export(PropertyHint.Layers2DRender',
	'export_layers_2d_physics':'Export(PropertyHint.Layers2DPhysics',
	'export_layers_2d_navigation':'Export(PropertyHint.Layers2DNavigation',
	'export_layers_3d_render':'Export(PropertyHint.Layers3DRender',
	'export_layers_3d_physics':'Export(PropertyHint.Layers3DPhysics',
	'export_layers_3d_navigation':'Export(PropertyHint.Layers3DNavigation',
	'export_layers_avoidance':'Export(PropertyHint.LayersAvoidance',
	'export_file':'Export(PropertyHint.File',
	'export_dir':'Export(PropertyHint.Dir',
	'export_global_file':'Export(PropertyHint.GlobalFile',
	'export_global_dir':'Export(PropertyHint.GlobalDir',
	'export_resource_type':'Export(PropertyHint.RessourceType',
	'export_multiline_text':'Export(PropertyHint.MultilineText',
	'export_expression':'Export(PropertyHint.Expression',
	'export_placeholder_text':'Export(PropertyHint.PlaceholderText',
	'export_color_no_alpha':'Export(PropertyHint.ColorNoAlpha',
	'export_object_id':'Export(PropertyHint.ObjectId',
	'export_type_string':'Export(PropertyHint.TypeString',
	'export_node_path_to_edited_nod':'Export(PropertyHint.NodePathToEditedNode',
	'export_object_too_big':'Export(PropertyHint.ObjectTooBig',
	'export_node_path_valid_types':'Export(PropertyHint.NodePathValidTypes',
	'export_save_file':'Export(PropertyHint.SaveFile',
	'export_global_save_file':'Export(PropertyHint.GlobalSaveFile',
	'export_int_is_objectid':'Export(PropertyHint.IntIsObjectId',
	'export_int_is_pointer':'Export(PropertyHint.IntIsPointer',
	'export_array_type':'Export(PropertyHint.ArrayType',
	'export_locale_id':'Export(PropertyHint.LocaleId',
	'export_localizable_string':'Export(PropertyHint.LocalizableString',
	'export_node_type':'Export(PropertyHint.NodeType',
	'export_hide_quaternion_edit':'Export(PropertyHint.HideQuaternionEdit',
	'export_password':'Export(PropertyHint.Password',
}

variable_replacements = {
	"self":"this",
	"PI":"Mathf.Pi",
	"TAU":"Mathf.Tau",
	"INF":"Mathf.Inf",
	"NAN":"Mathf.NaN",
	"TYPE_NIL":"null",
	"TYPE_OBJECT":"typeof(Godot.Object)",
	"TYPE_BOOL":"typeof(bool)",
	"TYPE_INT":"typeof(int)",
	"TYPE_REAL":"typeof(double)",
	"TYPE_RID":"typeof(RID)",
	"TYPE_STRING":"typeof(string)",
}
for missing_vt in (vt for vt in variant_types if vt not in variable_replacements):
	variable_replacements[missing_vt] = f'typeof(' + toPascal(missing_vt.replace('TYPE_', '').lower()) + ')'

function_replacements = {
	'range':'GD.Range',
	'preload': "/* preload has no equivalent, add a 'ResourcePreloader' Node in your scene */",
	'weakref': 'GodotObject.WeakRef(obj)',
	'instance_from_id' : 'GodotObject.InstanceFromId',
	'is_instance_id_valid' : 'GodotObject.IsInstanceIdValid',
	'is_instance_valid' : 'GodotObject.IsInstanceValid',
	'assert' : 'System.Diagnostics.Debug.Assert',
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
	'convert' : 'GD.Convert',
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
	'get_stack': 'System.Environment.StackTrace',
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
	'type_exists' : 'ClassDB.ClassExists',
	'type_string' : 'Variant.Type.ToString',
	'typeof' : 'Variant.VariantType',
	'var_to_bytes' : 'GD.VarToBytes',
	'var_to_bytes_with_objects' : 'GD.VarToBytesWithObjects',
	'var_to_str' : 'GD.VarToStr',
	'wrap' : 'Mathf.Wrap',
	'wrapf' : 'Mathf.Wrap',
	'wrapi' : 'Mathf.Wrap'
}