
# mock class, used to resolve classes using the parser

class Transpiler:
	
	def __init__(self):
		# used directly in parser at some point
		self.level = 0
	
	def current_class(self, class_name, klass):
		pass
	
	def define_class(self, name, base_class, is_tool, is_main):
		pass
	
	def enum(self, name, params, params_init):
		for i, (pName, pType) in enumerate(params.items()):
			if pName in params_init:
				get(params_init[pName])
	
	def annotation(self, name, params, memberName, endline):
		pass
	
	def declare_property(self, type, name, assignment, accessors, constant, static, onready):
		if assignment: get(assignment)
		if accessors:
			for accessor in accessors: pass
		
	def getter_method(self, member, getterName):
		pass
	
	def setter_method(self, member, setterName):
		pass
	
	def getter(self, member, code):
		pass
	
	def setter(self, member, valueName, code):
		pass
	
	def cleanGetSetCode(self, code, member):
		pass
	
	def declare_variable(self, type, name, assignment):
		if assignment: get(assignment)
	
	def define_method(self, name, params = {}, params_init = {}, return_type = None, code = '', static = False, override = False):
		for i, (pName, pType) in enumerate(params.items()):
			if pName in params_init:
				self += ' = '; get(params_init[pName])
	
	def define_signal(self, name, params):
		pass
	
	def assignment(self, exp):
		get(exp)
	
	def subexpression(self, expression):
		get(expression)
	
	def create_array(self, values):
		pass

	def array_item(self, item):
		get(item)
		
	def create_dict(self, values):
		pass

	def dict_item(self, key, value):
		get(key); get(value)
	
	def create_lambda(self, params, code):
		pass
	
	def literal(self, value):
		pass

	def string(self, value):
		pass
	
	def constant(self, name):
		pass
	
	def property(self, name):
		pass

	def variable(self, name):
		pass
	
	def singleton(self, name):
		pass
	
	def reference(self, name, obj_type, member_type, is_singleton = False):
		pass

	def reassignment(self, name, obj_type, member_type, is_singleton, op, val):
		get(val)
	
	def call(self, calling_type, name, params):
		for i, p in enumerate(params): get(p)
	
	def constructor(self, name, type, params):
		pass
	
	def subscription(self, key):
		get(key)
		
	def operator(self, op):
		pass
	
	def check_type(self, exp, checked):
		get(exp)
	
	def ternary(self, condition, valueIfTrue, valueIfFalse):
		get(condition); get(valueIfTrue); get(valueIfFalse)
	
	def returnStmt(self, return_exp):
		get(return_exp)
	
	def ifStmt(self, condition):
		get(condition)
	
	def elifStmt(self, condition):
		get(condition)
	
	def elseStmt(self):
		pass
	
	def whileStmt(self, condition):
		get(condition)
		
	def forStmt(self, name, type, exp):
		get(exp)
	
	def breakStmt(self):
		pass
	
	def continueStmt(self):
		pass
	
	def awaitStmt(self, object, signalName):
		pass
	
	def emitSignal(self, name, params):
		for i, p in enumerate(params):
			get(p)
	
	def connectSignal(self, name, params):
		get(params[0])
	
	def matchStmt(self, evaluated, cases):
		type = get(evaluated)
		get(evaluated)
		
		for pattern, when, code in cases():
			if pattern != 'default':
				get(pattern)
				if when: get(when)
	
	def end_class(self, name):
		pass
	
	def end_script(self):
		pass
	
	def comment(self, content):
		pass
	
	def multiline_comment(self, content):
		pass
	
	def end_statement(self):
		pass
	
	def __iadd__(self, txt):
		return self
	
	def write(self, txt):
		pass
	
	def get_result(self):
		return '' 
	
	def save_result(self):
		pass
	
	def UpScope(self):
		pass
	
	def DownScope(self):
		pass
	
	def getLayer(self):
		pass
	
	def addLayer(self):
		pass
		
	def popLayer(self):
		return ''

# trick for generator values
get = next