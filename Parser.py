import re
import os
from enum import IntFlag as Enum
from copy import copy

import godot_types as ref
from Tokenizer import Tokenizer

# TODO: reorganise methods to follow grammar

# recursive descent parser
class Parser:
	
	def __init__(self, filename, text, transpiler):
		# keep track of the script being transpiled
		self.script_name = filename
		
		# transpiler renamed 'out' for brevity
		self.out = transpiler
		
		# generator that splits text into tokens
		# adding an endline last to ensure we get the last token
		self.tokens = Tokenizer().tokenize(text)# + '\n')
		
		# update current token
		self.advance()
		
		# indentation level
		self.level = 0
		
		# script class data
		self.is_tool = None
		self.base_class = None
		self.class_name = None
		self.classData = None
	
	""" parsing utils """
	
	def advance(self):
		try:
			self.current = next(self.tokens)
		except StopIteration as err:
			# reached end of file
			# using a trick to allow parsing to finish properly
			self.current.type = 'EOF'
			self.current.value = 'EOF'
	
	# while implementation that avoids infinite loops
	def doWhile(self, condition):
		last = -1
		while self.current != last and condition():
			last = self.current;
			yield
	
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
		#print('+', found)
		return found
		
	def consumeUntil(self, token, separator = ''):
		result = []
		for i in self.doWhile(lambda : \
					not self.match_value(token) \
				and not self.match_type(token)):
			result.append(self.consume())
		return separator.join(result)
	
	
	# called when an endline is excpected
	def endline(self):
		lvl = 999
		jumpedLines = 0
		
		for i in self.doWhile(lambda:True):
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
				# automatically go down in scope if unexpected indentation
				while lvl < self.level:
					self.level -=1
					self.out.DownScope();
					#print("downscope    ", self.current)
				break
		
		self.out += '\n' * jumpedLines
	
	""" parsing / transpiling """
	
	FLAGS = Enum('FLAGS', ('none', 'static', 'constant', 'property')) 
	
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
			
			for i in self.doWhile(lambda:True):
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
		for i in self.doWhile(lambda:self.level >= class_lvl): self.class_body()
		
		# TODO : add nested class to godot_types
	
	
	# TODO: support enum as variable type, ex: "var v = MyEnum.FOO" => "MyEnum v = MyEnum.FOO;"
	# NOTE: enums have similar syntax in gdscript, C# and cpp
	# lazily passing the enum definition as-is for now
	def enum(self):
		name = self.consume() if self.match_type('TEXT') else ''
		definition = self.consumeUntil('}')
		definition += self.consume() # get the remaining '}'
		self.out.enum(name, definition)
	
	
	# Method -> func <name>(*<params>) [-> <type>]? :[Block]
	def method(self, static):
		name = self.consume()
		self.expect('(')
		
		params = {}
		params_init = {}
		
		# param -> <name> [: [<type>]?]? [= <Expression>]?
		for i in self.doWhile(lambda: not self.expect(')')):
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
	
	
	# class member 
	def member(self, static):
		
		# exports and such : @annotation[(params)]?
		# while is used to get out in case of on_ready
		is_onready = False
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
		if constant or self.expect('var'):
			self.declare( \
					 self.FLAGS.property \
				| (  self.FLAGS.constant if constant \
				else self.FLAGS.static if static \
				else self.FLAGS.none))
				# TODO : add 'exported' flag
		
			# TODO: handle get set
			
			self.out.end_statement()
	
	def declare(self, flags):
		name = self.consume()
		type = self.parseType() if self.expect(':') and self.match_type('TEXT') else None
		
		# parsing assignment if needed
		ass_generator = self.assignment()
		ass_type = next(ass_generator)
		
		# get type
		type = type or ass_type or 'Variant'
		# TODO: fix(?) -> locals are treated like members
		self.classData.members[name] = type
		
		# emit code
		if flags & self.FLAGS.property:
			self.out.declare_property(type, name, flags & self.FLAGS.constant, flags & self.FLAGS.static)
		else:
			self.out.declare_variable(type, name)
		next(ass_generator)
	
	# assignment and all expression use generator/passthrough for type inference
	# the format expected is :
	# yield <type>
	# <emit code>
	
	def assignment(self):
		exp = self.expression() if self.expect('=') else None
		if exp: yield next(exp); self.out.assignment(exp)
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
	#  |->Assignment      -> <Expression> = <Expression>                                        ----> TODO
	#  |->Expression (see after statement implementation)
	
	
	def Block(self):
	
		self.level += 1
		block_lvl = self.level
		
		self.out.UpScope()
		self.endline()
		
		stmts = []
		return_type = None
		
		for i in self.doWhile(lambda : self.level >= block_lvl):
			res = self.statement()
			return_type = return_type or res
			self.endline()
		
		return return_type

	def statement(self):
		if self.expect('pass'): return
		elif self.expect('var'): return self.declare(self.FLAGS.none)
		elif self.expect('if'): return #self.ifStmt()
		elif self.expect('while'): return #self.whileStmt()
		elif self.expect('for'): return #self.forStmt()
		elif self.expect('match'): return #self.matchStmt()
		elif self.expect('return'):return self.returnStmt()
		
		# NOTE: expression() handles function calls and modification operators (a += b)
		# even though it is not conceptually correct
		exp = self.expression(); next(exp)
		# assignment : <expression> = <expression>
		if self.match_value('='):
			ass = self.assignment(); next(ass)
			next(exp); next(ass)
		else: next(exp)
		self.out.end_statement()
	
	
	def returnStmt(self):
		exp = self.expression()
		type = next(exp)
		self.out.returnStmt(exp)
		self.out.end_statement()
		return type
	
	
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
	
	
	# convert to the way docs specify an array type
	def parseType(self):
		type = self.consume()
		if type == 'Array' and self.expect('['):
			type = self.consume() + '[]'
			self.expect(']')
		return type

## Utils

def passthrough(closure, *values):
	closure(*values); yield
