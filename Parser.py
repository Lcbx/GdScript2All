import re
import os
import godotReference as ref
from libs.sly import Lexer

# recursive descent parser
class Parser:
	class Tokenizer(Lexer):
		tokens = { COMMENT, LINE_END, TEXT, ARROW, FLOAT, INT, STRING, LONG_STRING, UNARY, COMPARISON, ARITHMETIC }
		literals = { '.', ':', '(', ')', '[', ']', '{', '}', '@', '$', '%', ',', '\\', '='}
		
		# ignore whitespace and carriage returns
		ignore = ' \r'
		
		# Token definitions
		ARROW = r'->'
		UNARY = r'(~|!|not){1}'
		COMPARISON = r'(==|!=|<=|>=|\|\||&&|<|>|and|or){1}'
		ARITHMETIC = r'(<<|>>|\*\*|\*|\+|-|\/|%|&|\^|\|){1}=?'
		
		TEXT = r'[a-zA-Z_][a-zA-Z0-9_]*'
		FLOAT = r'\d+[.](\d*)?|[.]\d+'
		INT = r'\d+'
		
		# expression broken to the next line
		@_(r'\\\n\t*')
		def ignore_line_break(self, t): self.update_lineno(t)
		
		
		# remove '#'
		@_(r'#.*')
		def COMMENT(self, t):
			t.value = t.value[1:]; return t
		
		# remove """"""
		@_(r'"""[\S\s]*?"""')
		def LONG_STRING(self, t):
			self.update_lineno(t);
			t.value = t.value[3:-3]; return t
		
		# remove "" and replace \" by "
		@_(r'"(.|\\")*?"|\'(.|\\\')*?\'')
		def STRING(self, t):
			self.update_lineno(t)
			t.value = t.value[1:-1].replace('\\'+t.value[0], t.value[0])
			return t
		
		# at endlines, count tabs for scope level
		@_(r'\n\t*')
		def LINE_END(self, t): self.update_lineno(t); t.value = str(t.value.count('\t')); return t
		
		def update_lineno(self, t): self.lineno += t.value.count('\n')
		def error(self, t):
			print("Illegal character '%s'" % t.value[0])
			self.index += 1
	
	def __init__(self, filename, text, transpiler):
		# keep track of the script being transpiled
		self.script_name = filename
		# transpiler renamed 'out' for brevity
		self.out = transpiler
		
		# split text into tokens
		self.tokens =  Parser.Tokenizer().tokenize(text)
		
		# current token
		self.current = next(self.tokens)
		self.consumed = None
		
		# indentation level
		self.level = 0
		
		# script class data
		self.is_tool = None
		self.base_class = None
		self.class_name = None
		self.data = ref.ClassData()
	
	
	""" parsing utils """
	
	def advance(self):
		if self.current != None: self.current = next(self.tokens)
	
	# avoid infinite loops
	def doWhile(self, condition, effect):
		last = -1
		while self.current != last and condition():
			last = self.current; effect()
	
	def match_type(self, *tokens):
		return any( [token == self.current.type for token in tokens] )
	
	def match_value(self, *tokens):
		return any( [token == self.current.value for token in tokens] )
	
	def expect(self, token):
		found = self.match_value(token)
		if found: self.advance()
		return found
	
	def consume(self):
		found = self.current.value
		self.advance()
		print('+', found)
		return found
		
	def consumeUntil(self, token):
		result = ''
		def accumulate(): nonlocal result; result += self.consume()
		self.doWhile(lambda : not self.match_value(token), accumulate)
		return result
	
	
	""" parsing / transpiling """
	
	# call when an endline is excpected
	def endline(self):
		lvl = -1
		keepLooping = True
		jumpedLines = 0
		
		def implementation():
			nonlocal lvl
			nonlocal keepLooping
			nonlocal jumpedLines
			
			# handle comments
			if self.match_type('COMMENT', 'LONG_STRING'):
				self.out += '\n' * jumpedLines
				jumpedLines = 0
				
				if self.match_type('COMMENT'):
					self.out.line_comment(self.consume())
				elif self.match_type('LONG_STRING'):
					self.out.multiline_comment(self.consume())
			
			# setting scope level only when we encounter non-whitespace
			if self.match_type('LINE_END'):
				lvl = int(self.consume())
				# add endline in generated code to match script
				jumpedLines += 1
			
			else:
				# go up and down in scope
				# NOTE: we assume scope is managed the same way across languages
				if lvl != -1:
					while lvl > self.level: self.out.UpScope(); self.level +=1
					while lvl < self.level: self.out.DownScope(); self.level -=1
				keepLooping = False
				return
		
		self.doWhile(lambda:keepLooping, implementation)
		self.out += '\n' * jumpedLines
	
	
	# convert to the way docs specify an array type
	def parseType(self):
		type = self.consume()
		if type == 'Array' and self.expect('['):
			type = self.consume() + '[]'
			self.expect(']')
		return type
	
	def transpile(self):
		
		# in case there is a file header / comments at start
		self.endline()
		
		# script start specific statements
		self.is_tool = self.expect('@') and self.expect('tool'); self.endline()
		self.base_class = self.consume() if self.expect('extends') else 'Object'; self.endline()
		self.class_name = self.consume() if self.expect('class_name') else self.script_name
		
		# no endline after class name since we declare the class before that
		self.out.define_class(self.class_name, self.base_class, self.is_tool); self.endline()
		
		# script-level loop
		for i in range(2):
			self.doWhile(lambda:True, self.class_body)
			
			# end of file
			if self.current == None: break
			
			# panic system : drop current line if we can't parse it
			else:
				token = self.current
				escaped = []
				while not self.match_type('LINE_END') and self.current :
					escaped.append(self.consume())
				escaped = ' '.join(escaped).replace('\n', '\\n')
				msg = f'PANIC! <{escaped}> unexpected at {token}'
				self.out.line_comment(msg)
				print('---------', msg)
				self.endline()
		
		# end script class
		self.out.DownScope()
		
		# tell the transpiler we're done
		self.out.end_script()
	
	
	def class_body(self):
		# gdscript 4 accepts nested classes
		if self.expect('class'): self.nested_class()
		elif self.expect('enum'): self.enum()
		elif self.expect('func'): self.method()
		else: self.member()
		# end statement
		self.endline()
	
	
	def nested_class(self):
		class_name = self.consume()
		base_class = self.consume() if self.expect('extends') else 'Object'
		# NOTE: can inner classes be tools ? are they the same as their script class ?
		self.out.define_class(class_name, base_class, False)
		self.expect(':')
		
		self.level += 1
		class_lvl = self.level
		# NOTE: technically there would be no annotations in inner classes
		self.doWhile(lambda:self.level >= class_lvl, self.class_body )
	
	
	# TODO: support enum as variable type, ex: "var v = MyEnum.FOO" => "MyEnum v = MyEnum.FOO;"
	# NOTE: enums have similar syntax in gdscript, C# and cpp
	# lazily passing the enum definition as-is for now
	def enum(self):
		name = self.consume() if self.match_type('TEXT') else ''
		definition = self.consumeUntil('}')
		definition += self.consume() # get the remaining '}'
		self.out.enum(name, definition)
	
	
	# Method -> func <name>(*<params>) [-> <type>]? :[Block]
	def method(self):
		name = self.consume()
		self.expect('(')
		
		params = {}
		params_init = {}
		
		# param -> <name> [: [<type>]?]? [= <Expression>]?
		def parseParam():
			name = self.consume()
			type = self.parseType() if self.expect(':') and self.match_type('TEXT') else 'Variant'
			init = self.expression() if self.expect('=') else None
			if init:
				initType = next(init)
				type = type or initType
				params_init[name] = initType
			self.expect(',')
			params[name] = type
			
		self.doWhile(lambda: not self.expect(')'), parseParam)
		
		returnType = self.parseType() if self.expect('->') else 'void'
		
		self.expect(':')
		
		# TODO : add an emit func to out
		self.out += f'{returnType} {name}(' + \
			','.join([ f'{pType} {pName}' \
			+ ( f'= {params_init[pName]}' if pName in params_init else '') \
			for pName, pType in params.items()]) + ')'
		
		# TODO: add params to locals
		# TODO!! find a way to infer method return type BEFORE emitting block code !
		blockType = self.Block()
		type = returnType or blockType or 'Variant'
		self.data.methods[name] = type
	
	
	# class member 
	def member(self):
		is_onready = False
		
		# exports and such : @annotation[(params)]?
		while self.expect('@'):
			
			# NOTE: special case for onready (needs moving the assignment into ready function)
			# TODO: call out.assignement with onready flag (later)
			if self.expect('on_ready'): is_onready = True; break
			
			name = self.consume()
			# NOTE: this should work for most cases
			params = self.consumeUntil(')') if self.expect('(') else ''
			if params:
				self.expect(')')
				params = params.replace('"', '').replace("'", '')
			self.out.annotation(name, params)
		
		# NOTE: constants should only be declared at script/inner class level
		# member : [[static]? var|const] variable_name [: [type]? ]? = expression
		constant = self.expect('const') 
		static = self.expect('static') 
		if constant or self.expect('var'):
			self.declare(constant, static)
		
		# TODO: handle get set
	
	def declare(self, constant = False, static = False):
		name = self.consume()
		type = self.parseType() if self.expect(':') and self.match_type('TEXT') else None
		
		# parsing assignment if needed
		ass_generator = self.assignment()
		ass_type = next(ass_generator)
		
		# get type
		type = type or ass_type or 'Variant'
		# TODO: fix(?) -> locals are treated like members
		self.data.members[name] = type 
		
		# emit code
		self.out.declare_variable(type, name, constant, static)
		next(ass_generator)
		self.out.end_statement()
	
	# assignment and all expression use generator/passthrough for type inference
	# the format expected is :
	# yield <type>
	# <emit code>
	
	def assignment(self):
		exp = self.expression() if self.expect('=') else None
		if exp: yield next(exp); self.out.assignment(); next(exp)
		else: yield
		yield
	
	## GRAMMAR
	
	# Script : [<Member>|<Method>]1+
	
	# Member -> [@<annotation>[(*<params>)]?]? <variable_declaration>
	# variable_declaration -> [const|[static]? var] <name> [:<type>]? [<Assignment>]?
	# Method -> func <name>(*<params>) [-> <type>]? :[Block]
	# Block -> <Statement>1+
	
	# Statement
	#  |->NoOperation     -> pass
	#  |->Declaration     -> var <variable> <Assignment>										----> TODO
	#  |->IfStatement     -> if <boolean>: <Block> [elif <boolean> <Block>]* [else <Block>]?    ----> TODO
	#  |->WhileStatement  -> while <boolean>: <Block>                                           ----> TODO
	#  |->ForStatement    -> for <variable> in <Expression> | : <Block>                         ----> TODO
	#  |->MatchStatement  -> match <Expression>: [<Expression>:<Block>]1+                       ----> TODO
	#  |->ReturnStatement -> return <Expression>                                                ----> TODO
	#  |->Assignment      -> <variable> = <Expression>                                          ----> TODO
	#  |->Expression (see after statement implementation)
	
	
	def Block(self):
		self.out.UpScope()
		self.level += 1
		block_lvl = self.level
		return_type = None
		
		def stmt():
			nonlocal return_type
			ret = self.statement()
			return_type = return_type or ret
			self.endline()
		
		self.doWhile(lambda : self.level >= block_lvl, stmt )
		
		return return_type
	
	def statement(self):
		if self.expect('pass'): pass
		elif self.expect('var'): self.declare()
		elif self.expect('if'): pass #self.ifStmt()
		elif self.expect('while'): pass #self.whileStmt()
		elif self.expect('for'): pass #self.forStmt()
		elif self.expect('match'): pass #self.matchStmt()
		elif self.expect('return'):pass # return self.returnStmt()
		
		# assignment
		elif self.current in self.data.members and self.current.endswith('='):
			name = self.consume()
			self.out.variable(name)
			ass = self.assigment(); next(ass); next(ass)
		
		# NOTE: lone function calls and modification operators (a += b) are handled in expression
		else: exp = self.expression(); next(exp); next(exp);
	
	
	# Expression	-> ternary
	# ternary		-> [boolean [if boolean else boolean]* ]
	# boolean		-> arithmetic [and|or|<|>|==|...  arithmetic]*
	# arithmetic	-> [+|-|~] value [*|/|+|-|... value]*
	# value			-> literal|subexpression|textCode
	# literal		-> int|float|string|array|dict
	# array			-> \[ [expresssion [, expression]*]? \]	
	# dict			-> { [expresssion:expression [, expresssion:expression]*]? }
	# subexpression	-> (expression)
	# textCode		-> variable|reference|call|subscription
	# variable		-> <name>
	# reference		-> textCode.textCode
	# call			-> textCode([*params]?)
	# subscription	-> textcode[<index>]
	
	def expression(self):
		return self.ternary()
	
	
	def ternary(self):
		cmp1 = self.boolean()
		yield next(cmp1)
		if self.expect('if'):
			cmp2 = self.boolean(); next(cmp2)
			self.expect('else')
			ter2 = self.ternary(); next(ter2)
			self.out.ternary(cmp2, cmp1, ter2)
		else:
			next(cmp1)
		yield
	
	# mixing boolean and comparison for simplicity
	def boolean(self):
		ar1 = self.arithmetic()
		ar_type = next(ar1)
		
		op = self.consume() if self.match_type('COMPARISON') else None
		
		if op:
			ar2 = self.boolean()
			ar_type = next(ar2)
			yield 'bool'
			next(ar1)
			self.out.operator(op)
			next(ar2)
		else:
			yield ar_type
			next(ar1)
		yield
	
	
	def arithmetic(self):
		
		# unary operator ex: i = -4
		pre_op = self.consume() if self.match_type('UNARY') else None
		
		ar = self._arithmetic()
		yield next(ar);
		if pre_op: self.out.operator(pre_op)
		next(ar); yield
	
	def _arithmetic(self):
		value1 = self.value()
		value_type = next(value1)
		
		# NOTE: we accept arithmetic reassignment ex: i += 1
		# which is not exact but simpler to do this way
		op = self.consume() if self.match_type('ARITHMETIC') else None
		
		if op:
			value2 = self._arithmetic()
			value_type = next(value2)
			yield value_type
			next(value1)
			self.out.operator(op)
			next(value2)
		else:
			yield value_type
			next(value1)
		yield
		
	
	def value(self):
		
		# int
		if self.match_type('INT'):
			val = int(self.consume())
			yield 'int'
			self.out.literal(val)
			
		# float
		elif self.match_type('FLOAT'):
			val = float(self.consume())
			yield 'float'
			self.out.literal(val)
			
		# bool
		elif self.current.value in ('true', 'false'):
			val = self.consume() == 'true'
			yield 'bool'
			self.out.literal(val)
		
		# multiline (""") string
		elif self.match_type('LONG_STRING'):
			val = self.consume()
			yield 'string'
			self.out.literal(val)
		# "" or '' string
		elif self.match_type('STRING'):
			val = self.consume()
			yield 'string'
			self.out.literal(val)
			
		# array
		elif self.expect('['):
			yield 'Array'
			def iter():
				while not self.expect(']'):
					val = self.expression();
					next(val) # discarding type
					self.expect(',')
					yield val
			values = [*iter()]
			self.out.create_array(values)
			
		# dictionary
		elif self.expect('{'):
			yield 'Dictionary'
			def iter():
				while not self.expect('}'):
					key = self.expression()
					val = self.expression()
					next(key); self.expect(':'); next(val)
					self.expect(',')
					yield (key, val)
			kv = [*iter()]
			self.out.create_dict(kv)
			
		# subexpression : (expression)
		elif self.expect('('):
			enclosed = self.expression()
			yield next(enclosed)
			self.out.subexpression(enclosed)
			self.expect(')')
		
		# get_node shortcuts : $node => get_node("node") -> Node
		elif self.expect('$'):
			name = self.consume()
			yield 'Node'
			self.out.call("get_node", (passthrough(self.out.literal, name) ,) )
			
		# scene-unique nodes : %node => get_node("%node") -> Node
		elif self.expect('%'):
			name = self.consume()
			yield 'Node'
			self.out.call("get_node", (passthrough(self.out.literal, f'%{name}') ,) )
		
		# textCode : variable|reference|call
		elif self.match_type('TEXT'):
			content = self.textCode()
			yield next(content)
			next(content)
		
		yield; yield
	
	# textCode : variable|call|reference
	def textCode(self):
		
		name = self.consume()
		
		# self. is essentially just syntactic in most languages
		this = name == 'self' and self.expect('.')
		if this: name = self.consume()
		
		# type could be a singleton (ex: RenderingServer) or a call to a static function
		singleton = name in ref.godot_types
		type = self.data.members.get(name, None) or (name if singleton else None)
		
		# call
		if self.expect('('):
			call = self.call(None, name)
			yield next(call)
			if this: self.out.this()
			next(call)
		
		# reference
		elif self.expect('.'):
			reference = self.reference(type)
			yield next(reference)
			if this: self.out.this()
			self.out.singleton(name) if singleton else self.out.variable(name)
			next(reference)
		
		# subscription
		elif self.expect('['):
			s = self.subscription(type)
			yield next(s)
			if this: self.out.this()
			self.out.variable(name)
			next(s)
		
		# lone variable or global
		else:
			yield self.data.members.get(name, None)
			if this: self.out.this()
			self.out.variable(name)
		yield
	
	
	def call(self, type, name):
		
		# determine return type
		constructor = name in ref.godot_types
		type = name if constructor \
			else self.data.methods[name] if name in self.data.methods \
			else ref.godot_types[type].methods[name] if \
				type in ref.godot_types and name in ref.godot_types[type].methods \
			else None
		
		# emission of code 
		emit = lambda : self.out.constructor(name, params) if constructor else self.out.call(name, params)
		
		# determine params
		def iter():
			while not self.expect(')'):
				exp = self.expression(); next(exp); yield exp
				self.expect(',')
		params = ( *iter() ,)
		
		# reference
		if self.expect('.'):
			r = self.reference(type)
			yield next(r)
			emit()
			next(r)
		
		# subscription
		elif self.expect('['):
			s = self.subscription(type)
			yield next(s)
			emit()
			next(s)
		
		# end
		else:
			yield type
			emit()
		yield
	
	
	def reference(self, type):
		name = self.consume()
		member_type = ref.godot_types[type].members[name] if \
				type in ref.godot_types and name in ref.godot_types[type].members \
			else None
		
		# call
		if self.expect('('):
			call = self.call(type, name)
			yield next(call)
			# emit '.' while call() emits <name>(...)
			self.out.reference('') 
			next(call)
		
		# other reference
		elif self.expect('.'):
			r = self.reference(member_type)
			yield next(r)
			self.out.reference(name)
			next(r)
		
		# subscription
		elif self.expect('['):
			s = self.subscription(type)
			yield next(s)
			self.out.reference(name)
			next(s)
		
		# could be a constant
		elif type and name in ref.godot_types[type].constants:
			yield ref.godot_types[type].constants[name]
			self.out.constant(name)
		
		# end leaf
		else:
			yield member_type
			self.out.reference(name)
		yield
	
	
	def subscription(self, type):
		# NOTE: we only deternmine the type if it's a typed array
		type = type.replace('[]', '') if type and '[]' in type else None
		key = self.expression();next(key)
		self.expect(']')
		
		# call
		if self.expect('('):
			call = self.call(type, '')
			yield next(call)
			next(call)
		
		# reference
		elif self.expect('.'):
			refer = self.reference(type)
			yield next(refer)
			self.out.subscription(key)
		
		# end leaf
		else:
			yield type
			self.out.subscription(key)
		yield

## Utils

def passthrough(closure, *values):
	closure(*values); yield
