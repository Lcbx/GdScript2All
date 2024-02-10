import re
import os
from enum import IntFlag as Enum
from copy import copy

import godot_types as ref
from Tokenizer import Tokenizer


# TODO: FIX: method return inference not wortking ?
# TODO: support enum as variable type, ex: "var v = MyEnum.FOO" => "MyEnum v = MyEnum.FOO;"

# TODO: support match statment
# TODO: support break|continue statments
# TODO: support 'as' keyword
# TODO: await => await ToSignal(....)"
# TODO: support adding user-defined classes to ref.godot_type
# TODO: Rename {Builtin_Class}.aa_bb_cc to AaBbCc (Eg Engine.is_editor_hint)

# TODO: support special literals like:
# * floating exponents : 58e-10
# * base16 int : 0x8E
# * bineary int : 0b1010
# * raw strings : r"hello"
# * string names : &"name"
# * nodepath : ^"parent/child"

# recursive descent parser
class Parser:
	
	def __init__(self, filename, text, transpiler):
		# keep track of the script being transpiled
		self.script_name = filename
		
		# transpiler renamed 'out' for brevity
		self.out = transpiler
		
		# generator that splits text into tokens
		self.tokenizer = Tokenizer()
		self.tokens = self.tokenizer.tokenize(text)
		
		# update current token
		self.advance()
		
		# indentation level
		self.level = 0
		
		# script class data
		self.is_tool = None
		self.base_class = None
		self.class_name = None
		self.classData = None
	
	
	""" SCRIPT/STATEMENT GRAMMAR 
	
	transpile : [<Member>|<Method>]1+
	
	Member -> <annotation>? <property>
	annotation -> @<name>[(*<params>)]?
	property -> [const|[static]? var] <name> [:<type>]? [<Assignment>]?
	Method -> func <name>(*<params>) [-> <type>]? :[Block]
	Block -> <Statement>1+
	
	Statement
	 |->NoOperation     -> pass
	 |->Declaration     -> var <variable> <Assignment>
	 |->IfStatement     -> if <boolean>: <Block> [elif <boolean> <Block>]* [else <Block>]?    ----> TODO
	 |->WhileStatement  -> while <boolean>: <Block>                                           ----> TODO
	 |->ForStatement    -> for <variable> in <Expression> | : <Block>                         ----> TODO
	 |->MatchStatement  -> match <Expression>: [<Expression>:<Block>]1+                       ----> TODO
	 |->ReturnStatement -> return <Expression>
	 |->Assignment      -> <Expression> = <Expression>
	 |->Expression (see after statement implementation)
	
	Expression grammar defined later
	
	"""
	
	def transpile(self):
		# in case there is a file header / comments at start
		self.endline()
		
		# script start specific statements
		self.is_tool = self.expect('@') and self.expect('tool'); self.endline()
		self.base_class = self.consume() if self.expect('extends') else 'Object'; self.endline()
		self.class_name = self.consume() if self.expect('class_name') else self.script_name
		
		# initialize script class data
		self.classData = copy(ref.godot_types[self.base_class])
		#print(self.classData.__dict__)
		
		# no endline after class name since we declare the class before that
		self.out.define_class(self.class_name, self.base_class, self.is_tool); self.endline()
		
		# script-level loop
		for i in range(2):
			
			for _ in self.doWhile(lambda:True):
				self.class_body()
			
			# get out if EOF reached
			if self.match_type('EOF'):
				print("reached EOF")
				break
			
			# panic system :
			# drop current line if we can't parse it
			
			token = self.current
			escaped = self.consumeUntil('LINE_END', separator=' ').replace('\n', '\\n')
			self.endline()
			
			msg = f'PANIC! <{escaped}> unexpected at {token}'
			self.out.line_comment(msg)
			print('---------', msg)
		
		# tell the transpiler we're done
		self.out.end_script()
	
	
	def class_body(self):
		# gdscript 4 accepts nested classes
		static = self.expect('static')
		if self.expect('class'): self.nested_class()
		elif self.expect('enum'): self.enum()
		elif self.expect('func'): self.method(static)
		else: self.member(static)
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
		for _ in self.doWhile(lambda:self.level >= class_lvl): self.class_body()
		
		# TODO : add nested class to godot_types
	
	
	def enum(self):
		# NOTE: enums have similar syntax in gdscript, C# and cpp
		# lazily passing the enum definition as-is for now
		name = self.consume() if self.match_type('TEXT') else ''
		definition = self.consumeUntil('}')
		definition += self.consume() # get the remaining '}'
		self.out.enum(name, definition)
	
	
	DECL_FLAGS = Enum('DECL_FLAGS', ('none', 'static', 'constant', 'property', 'onready')) 
	
	# class member
	def member(self, static):
		
		onready = False
		
		# exports and such : @annotation[(params)]?
		# while is used to get out in case of on_ready
		annotation = None
		params = ''
		while self.expect('@'):
			
			# NOTE: special case for onready (needs moving the assignment into ready function)
			# TODO: call out.assignement with onready flag (later)
			if self.expect('on_ready'): onready = True; break
			
			annotation = self.consume()
			# NOTE: this should work for most cases
			if self.expect('('):
				params = self.consumeUntil(')').replace('"', '').replace("'", '')
				self.expect(')')
			self.endline()
		
		# member : [[static]? var|const] variable_name [: [type]? ]? = expression
		constant = self.expect('const')
		if constant or self.expect('var'):
			member = self.consume()
			if annotation: self.out.annotation(annotation, params, member)
			self.declare( member, \
					 self.DECL_FLAGS.property \
				| (  self.DECL_FLAGS.constant if constant \
				else self.DECL_FLAGS.static if static \
				else self.DECL_FLAGS.onready if onready \
				else self.DECL_FLAGS.none))
			# TODO: handle get set
			self.out.end_statement()
	
	
	# Method -> func <name>(*<params>) [-> <type>]? :[Block]
	def method(self, static):
		name = self.consume()
		self.expect('(')
		
		params = {}
		params_init = {}
		
		# param -> <name> [: [<type>]?]? [= <Expression>]?
		for _ in self.doWhile(lambda: not self.expect(')')):
			pName = self.consume()
			pType = self.parseType() if self.expect(':') and self.match_type('TEXT') else None
			
			# initial value
			pInit = self.expression() if self.expect('=') else None
			if pInit:
				initType = next(pInit)
				pType = pType or initType
				params_init[pName] = pInit
			
			pType = pType or 'Variant'
			self.expect(',')
			params[pName] = pType
		
		# TODO: add params to locals
		
		returnType = self.parseType() if self.expect('->') else None
		
		self.expect(':')
		
		# make transpiler write to a buffer
		# so we can parser block code, emit declaration then emit block code
		self.out.addLayer()
		
		blockType = self.Block()
		
		returnType = returnType or blockType
		self.classData.methods[name] = returnType
		
		self.out.define_method(name, params, params_init, returnType, static)
	
	
	def Block(self):
		self.level += 1
		block_lvl = self.level
		return_type = None
		
		self.out.UpScope()
		
		for _ in self.doWhile(lambda : self.level >= block_lvl):
			res = self.statement()
			return_type = return_type or res
			self.endline()
		
		return return_type
	
	
	def statement(self):
		if self.expect('pass'): return
		elif self.expect('var'): return self.declare(flags=self.DECL_FLAGS.none)
		elif self.expect('if'): return #self.ifStmt()
		elif self.expect('while'): return #self.whileStmt()
		elif self.expect('for'): return #self.forStmt()
		elif self.expect('match'): return #self.matchStmt()
		elif self.expect('return'):return self.returnStmt()
		elif not self.match_type('LINE_END', 'COMMENT', 'LONG_STRING'):
			return self.reassign()
	
	
	def declare(self, name = None, flags = DECL_FLAGS.none):
		if not name: name = self.consume()
		type = self.parseType() if self.expect(':') and self.match_type('TEXT') else None
		
		# parsing assignment if needed
		ass = self.assignment( \
				name if flags & self.DECL_FLAGS.onready else None \
			) if self.expect('=') else None
		if ass:
			ass_type = next(ass)
			type = type or ass_type
		
		type = type or 'Variant'
		
		# emit code
		if flags & self.DECL_FLAGS.property:
			self.classData.members[name] = type
			self.out.declare_property(type, name, \
				flags & self.DECL_FLAGS.constant, \
				flags & self.DECL_FLAGS.static)
		else:
			# TODO: keep track of locals
			self.out.declare_variable(type, name)
		
		if ass: next(ass)
	
	
	def returnStmt(self):
		exp = self.expression()
		type = next(exp)
		self.out.returnStmt(exp)
		self.out.end_statement()
		return type
	
	
	# reassign : <expression> = <expression>
	def reassign(self):
		# NOTE: expression() handles function calls and modification operators (a += b)
		# even though it is not conceptually correct
		exp = self.expression(); next(exp)
		
		if self.expect('='):
			ass = self.assignment()
			next(ass); next(exp); next(ass)
		else: next(exp)
		self.out.end_statement()
	
	
	""" EXPRESSION GRAMMAR
	
	all expressions (+ assignment sub-statement) use generators for type inference
	the format expected is :
		yield <type>
		<emit code>
		yield
	
	Expression		-> ternary
	ternary			-> [boolean [if boolean else boolean]* ]
	boolean			-> arithmetic [and|or|<|>|==|...  arithmetic]*
	arithmetic		-> [+|-|~] value [*|/|+|-|... value]*
	value			-> literal|subexpression|textCode
	literal			-> int|float|string|array|dict
	array			-> \[ [expresssion [, expression]*]? \]	
	dict			-> { [expresssion:expression [, expresssion:expression]*]? }
	subexpression	-> (expression)
	textCode		-> variable|reference|call|subscription
	variable		-> <name>
	reference		-> textCode.textCode
	call			-> textCode([*params]?)
	subscription	-> textcode[<index>]
	
	"""
	
	def assignment(self, onreadyName = None):
		exp = self.expression()
		yield next(exp);
		self.out.assignment(exp, onreadyName)
		yield
	
	
	def expression(self):
		return self.ternary()
	
	def ternary(self):
		valTrue = self.boolean(); yield next(valTrue)
		if self.expect('if'):
			# NOTE: nested ternary bug if passed in another way
			def impl():
				cond = self.boolean(); next(cond)
				yield next(cond)
				self.expect('else')
				valFalse = self.ternary(); next(valFalse)
				yield next(valTrue)
				yield next(valFalse)
			self.out.ternary(impl())
		else: next(valTrue)
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
		next(ar)
		yield
	
	
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
		else: yield
		yield
	
	
	# textCode : variable|call|reference
	def textCode(self):
		
		name = self.consume()
		
		# self. is essentially just syntactic in most languages
		this = name == 'self' and self.expect('.')
		if this: name = self.consume()
		
		# type could be a singleton (ex: RenderingServer) or a call to a static function
		singleton = name in ref.godot_types
		type = self.classData.members.get(name, None) or (name if singleton else None)
		
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
			yield self.classData.members.get(name, None)
			if this: self.out.this()
			self.out.variable(name)
		yield
	
	
	def call(self, type, name):
		
		# determine return type
		constructor = name in ref.godot_types
		type = name if constructor \
			else self.classData.methods[name] if name in self.classData.methods \
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
	
	
	""" parsing utils """
	
	def advance(self):
		try:
			self.current = next(self.tokens)
		except StopIteration as err:
			# reached end of file
			# using a trick to finish parsing
			self.current.type = 'EOF'
			self.current.value = 'EOF'
	
	# while implementation that avoids infinite loops
	def doWhile(self, condition):
		last = -1
		while self.current != last and condition():
			last = self.current; yield
	
	def match_type(self, *tokens):
		return any( (token == self.current.type for token in tokens) )
	
	def match_value(self, *tokens):
		return any( (token == self.current.value for token in tokens) )
	
	def expect(self, token):
		found = self.match_value(token)
		if found: self.advance()
		return found
	
	def consume(self):
		found = self.current.value
		self.advance()
		#print('+', found)
		return found
	
	# parse type string and format it the way godot docs do
	def parseType(self):
		type = self.consume()
		# Array[type] => type[]
		if type == 'Array' and self.expect('['):
			type = self.consume() + '[]'
			self.expect(']')
		return type
		
	def consumeUntil(self, token, separator = ''):
		result = []
		for _ in self.doWhile(lambda : \
					not self.match_value(token) \
				and not self.match_type(token)):
			result.append(self.consume())
		return separator.join(result)
	
	
	# called when an endline is excpected
	def endline(self):
		lvl = 0
		jumpedLines = 0
		
		for _ in self.doWhile(lambda:True):
			
			# stub
			emitComments = (lambda : None)
			
			# setting scope level only when we encounter non-whitespace
			if self.match_type('LINE_END'):
				lvl = int(self.consume())
				jumpedLines += 1
			
			# parse comments
			elif self.match_type('COMMENT', 'LONG_STRING'):
				emit = self.out.line_comment if self.match_type('COMMENT') else self.out.multiline_comment
				content = self.consume()
				# override emitComments stub
				def emitComments(): emit(content)
			
			# found code, indentation now matters
			if not self.match_type('LINE_END'):
				while lvl < self.level:
					self.level -=1
					# NOTE: for prettier output, we emit downscope directly
					self.out.DownScope();
					#print("downscope    ", self.current)
				emitComments(); break
			
			# emit comment and continue loop
			else: emitComments()
		
		self.out += '\n' * jumpedLines

def passthrough(closure, *values):
	closure(*values); yield
