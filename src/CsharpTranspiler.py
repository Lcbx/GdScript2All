from io import StringIO as stringBuilder
import src.godot_types as ref


class Transpiler:
	
	def __init__(self, vprint):
		
		# verbose printing
		self.vprint = vprint
		
		# scope level
		self.level = 0
		
		# allows to parse code and rearrange it
		self.layers = [stringBuilder()]
		
		# default imports
		self += ref.header
		
		# onready assignments that need to be moved to the ready function
		self.onready_assigns = []
		
		# unnamed enums don't exist in C#, so we use a counter to give them a name
		self.unnamed_enums = 0
		
		# members names and types
		self.members = {}
		self.methods = {}
	
	def define_class(self, name, base_class, is_tool):
		if is_tool: self += '[Tool]\n'
		if base_class in ref.godot_types: base_class = f'Godot.{base_class}'
		self += f'public partial class {name} : {base_class}'
		self.UpScope()
		self += '\n'
	
	# NOTE: enums have similar syntax in gdscript, C# and cpp
	# lazily passing the enum definition as-is for now
	def enum(self, name, definition):
		# unnamed enums not supported in C#
		if not name:
			name  = f'Enum{self.unnamed_enums}'; self.unnamed_enums += 1
		self += f'public enum {name} {definition}'
	
	def annotation(self, name, params, memberName):
		# TODO: check replacements are exhaustive
		# https://docs.godotengine.org/en/stable/tutorials/scripting/gdscript/gdscript_exports.html
		# https://docs.godotengine.org/en/stable/tutorials/scripting/c_sharp/c_sharp_exports.html
		name = ref.export_replacements[name] if name in ref.export_replacements else toPascal(name) + (params and '(')
		self += f'[{name}"{params}")]' if params else f'[{name}]'
		self += '\n'
		
		# NOTE: might be a good idea to save exported members names
		# so we can generate bindings in c++
		if 'export' in name: pass
	
	def declare_property(self, type, name, constant, static):
		type = translate_type(type)
		const_decl = 'const ' if constant else 'static ' if static else ''
		exposed = 'protected' if name[0] == '_' else 'public'
		self += f'{exposed} {const_decl}{type} {name}'
		self.members[name] = type
	
	def setget(self, member, accessors):
		self.addLayer()
		self.UpScope()
		self += '\n'
		last_accessor = None
		
		# call the appropriate Transpiler method (defined afterward)
		for accessor in accessors:
			last_accessor = accessor
			params = accessor.split('/')
			method = getattr(self,params[0])
			method(member, *params[1:])
		
		# add mssing bracket when using a method as last accesor
		if 'method' in last_accessor:
			self.level -= 1;
			self += '\n}'
		# otherwise an extra downscope was done already
		
		code = self.popLayer()
		
		# add private property if missing
		if not asPrivate(member) in self.members:
			privateMember = '}\n' + '\t' * self.level + \
				f'private {self.members[member]} {asPrivate(member)};\n'
			code = rReplace(code, '}', privateMember)
		
		# this is for prettiness
		code = code.replace('\t' * (self.level+1) + '\n', '')
		self.write(code)
		
		
	def getter_method(self, member, getterName):
		self += f'get => {getterName}();\n'
	
	def setter_method(self, member, setterName):
		self += f'set => {setterName}(value);\n'
	
	def getter(self, member):
		code = self.popLayer()
		self += 'get';
		code = self.cleanGetSetCode(code, member)
		self.write(code)
	
	def setter(self, member, valueName):
		code = self.popLayer()
		self += 'set';
		code = self.cleanGetSetCode(code, member)
		self.write(code.replace(valueName, 'value'))
	
	def cleanGetSetCode(self, code, member):
		# use private value
		if not asPrivate(member) in self.members:
			code = code.replace(member, asPrivate(member))
		return code

	
	def declare_variable(self, type, name):
		self += f'var {name}'
	
	def define_method(self, name, params = {}, params_init = {}, return_type = None, static = False):
		
		return_type = translate_type(return_type)
		
		self.methods[name] = return_type
		
		blockText = self.popLayer()
		
		exposed = 'protected' if name[0] == '_' else 'public'
		static_str = 'static ' if static else ''
		self += f'{exposed} {static_str}{return_type} {name}('
		
		for i, (pName, pType) in enumerate(params.items()):
			if i != 0: self += ', '
			self += f'{translate_type(pType)} {pName}'
			if pName in params_init:
				self += ' = '; get(params_init[pName])
		
		self += ')'
		
		# add onready assignments if method is script-level _ready
		if name == '_ready' and self.level == 1:
			onreadies = '{' + ''.join(map(lambda stmt: f'\n\t\t{stmt};', self.onready_assigns))
			blockText = blockText.replace('{', onreadies, 1)
			self.onready_assigns.clear()
		
		self.write(blockText)
	
	def define_signal(self, name, params):
		paramStr = ','.join( ( f'{translate_type(pType)} {pName}' for pName, pType in params.items()))
		self += '[Signal]\n'
		self += f'public delegate void {name}Handler({paramStr});'
	
	def assignment(self, exp, onreadyName):
		if onreadyName:
			self.addLayer()
			self.write(f'{onreadyName} = '); get(exp)
			self.onready_assigns.append(self.popLayer())
			return
		self += ' = '; get(exp)
	
	def subexpression(self, expression):
		self += '('; get(expression); self += ')'
	
	def create_array(self, values):
		self += 'new Array{'
		for value in values:
			get(value); self += ','
		self += '}'
		
	def create_dict(self, kv):
		self += 'new Dictionary{'
		for key, value in kv:
			self += '{'; get(key); self += ','; get(value); self+= '},'
		self += '}'
	
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
	
	def variable(self, name):
		name = 'this' if name == 'self' else name
		self += name
	
	def singleton(self, name):
		self += translate_type(name)
	
	def reference(self, name):
		self += '.' + name
	
	def call(self, name, params):
		self += name + '('
		for i, p in enumerate(params):
			if i>0: self += ','
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
	
	def end_script(self):
		# add ready function if there are onready_assigns remaining
		if self.onready_assigns:
			# NOTE : if there are onready properties before and after a user-defined _ready method
			# this will result in 2 _ready functions in generated code
			self.addLayer()
			self += '\n{\n}'
			self.define_method('_ready')
		
		# TODO: in cpp, add member and method bindings
		
		# close remaining scopes (notably script-level class)
		while len(self.layers) > 1: self.write(self.popLayer())
		while self.level > 0: self.DownScope()
	
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
		return self.getLayer().getvalue()
	
	def save_result(self, outname):
		if not outname.endswith('.cs'): outname += '.cs'
		with open(outname,'w+') as wf:
			wf.write(self.get_result())
	
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
		self.layers.append(stringBuilder())
		
	def popLayer(self):
		# add top scope txt to lower then remove top
		scope = self.layers[-1].getvalue()
		self.layers.pop()
		return scope

def rReplace(string, toReplace, newValue, n = 1):
	return newValue.join(string.rsplit(toReplace,n))

def asPrivate(name):
	return '_' + name

def toPascal(text):
	text0is_ = text[0] == '_'
	if text0is_: text[0] = '*' # trick to preserve first underscore
	val = text.replace("_", " ").title().replace(" ", "")
	if text0is_: val[0] = '_'
	return val

def translate_type(type):
	if type == None: return 'void'
	if type in ['Array', 'Dictionary']: return type
	if type in ref.godot_types: return f'Godot.{type}'
	if type.endswith('[]'): return f'Array<{type[:-2]}>'
	if type == 'float': return 'double' # C# uses doubles
	return type

# trick for generator values
get = next