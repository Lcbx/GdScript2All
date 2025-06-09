import re
import os
from copy import copy
from enum import IntFlag as Flags

from Tokenizer import Tokenizer
from ClassData import ClassData

# NOTE: we add locally defined classes to godot_types
# to avoid having to join definitions
from godot_types import godot_types, GLOBALS, toSignalType, toEnumType


# recursive descent parser
class Parser:
	
	def __init__(self, filename, text, transpiler, vprint):
		# keep track of the script being transpiled
		self.script_name = filename
		
		# transpiler renamed 'out' for brevity
		self.out = transpiler
		
		# verbose printing
		self.vprint = vprint
		
		# generator that splits text into tokens
		self.tokenizer = Tokenizer()
		self.tokens = self.tokenizer.tokenize(text + '\n')
		
		# update current token
		self.advance()
		
		# indentation level
		self.level = 0
		
		# script class data
		self.is_tool = None
		self.class_name = None
		
		# class names in order of definition in file
		self.classes = []
		
		# local variables (name:type)
		self.locals = {}

		# in a subexpression "(<expression>)"
		self.in_subexpression = False
	
	""" SCRIPT/STATEMENT GRAMMAR 
	
	transpile : [<Member>|<Method>|<Signal>]*
	
	Member -> <annotation>? <property>
	annotation -> @<name>[(*<params>)]?
	property -> [const|[static]? var] <name> [:<type>]? [<Assignment>]? <setget>?
	Method -> func <name>(*<params>) [-> <type>]? :[Block]
	Signal -> signal name [(*params)]?
	Block -> <Statement>1+
	params -> <name> [: <type>]? [, params]*
	setget -> : [get [= <method_name>]|[ : Block ]]?, [set [= <method_name>]|[ : Block ]]?
	
	Statement
	 |->NoOperation     -> pass
	 |->Declaration     -> var <variable> <Assignment>
	 |->IfStatement     -> if <boolean>: <Block> [elif <boolean> <Block>]* [else <Block>]?
	 |->WhileStatement  -> while <boolean>: <Block>
	 |->ForStatement    -> for <variable> in <Expression> | : <Block>
	 |->MatchStatement  -> match <Expression>: [<Expression>:<Block>]1+
	 |->ReturnStatement -> return <Expression>
	 |->Reassign    -> Expression (see after statement implementation)
	
	Expression grammar defined later
	
	"""
	
	def transpile(self):
	
		# in case there is a file header / comments at start
		self.endline()
		
		# script start specific statements
		self.is_tool = self.expect('@', 'tool'); self.endline()
		class_name = self.script_name
		base_class = 'Object'
		# NOTE: parsing class_name twice, to allow any order of class_name/extends statements
		if self.expect('class_name'): class_name = self.consume(); self.endline()
		if self.expect('extends'): base_class = self.consume(); self.endline()
		if self.expect('class_name'): class_name = self.consume()
		
		# initialize script class data
		self.add_class(class_name, base_class, is_main = True); self.endline()
		
		# script-level loop
		tries = 0
		for _ in self.doWhile(lambda:tries<20):
			tries += 1

			self.class_body()
				
			# get out if reached end of file (EOF)
			if self.match_type('EOF'): self.vprint("reached EOF"); break
			
			# panic system : drop current line if we can't parse it
			token = self.current
			escaped = self.consumeUntil('LINE_END', separator=' ')
			self.level = int(self.consume())

			# add comment to output + print red warning in console output
			msg = f'PANIC! <{escaped}> unexpected at {token}'
			self.out.comment(f'{msg}\n')

			print(f'\033[91m{msg}\033[0m')

			# there's a good chance that the error occured inside a block
			self.level = max(0, self.level -1); self.Block()
		
		# tell the transpiler we're done
		self.out.end_script()
	
	
	def class_body(self):
		class_lvl = self.level
		for _ in self.doWhile(lambda:self.level >= class_lvl):
			if self.expect('pass'): return
			static = self.expect('static')
			if self.expect('class'): self.nested_class()
			elif self.expect('enum'): self.enum()
			elif self.expect('func'): self.method(static)
			elif self.expect('signal'): self.signal()
			else: self.member(static)
			self.endline()
	
	
	def nested_class(self):
		class_name = self.consume()
		base_class = self.consume() if self.expect('extends') else 'Object'
		# NOTE: can inner classes be tools ? are they the same as their script class ?
		self.add_class(class_name, base_class)
		self.expect(':')
		
		self.level += 1
		self.class_body()
		
		self.end_class()
	
	
	def enum(self):
		name = self.consume() if self.match_type('TEXT') else ''
		self.expect('{')
		# recycling method param definition parsing
		params, params_init = self.parseParamDefinition('}')

		for e_val in params.keys():	self.getClass().enums[ e_val ] = toEnumType(name)
		self.out.enum(name, params, params_init)
	
	
	DECL_FLAGS = Flags('DECL_FLAGS', ('none', 'static', 'constant', 'property', 'onready')) 
	
	# class member
	def member(self, static):
		
		onready = False
		
		# exports and such : @annotation[(params)]?
		# while is used to get out in case of on_ready
		annotation = None 
		ann_params = ''
		ann_endline = ''
		while self.expect('@'):
			
			# NOTE: special case for onready (needs moving the assignment into ready function)
			if onready := self.expect('onready'): self.endline(); break
			
			annotation = self.consume()
			# NOTE: this should work for most cases
			if self.expect('('): ann_params = self.consumeUntil(')').replace('"', '').replace("'", ''); self.expect(')')
			else: ann_params = ''
			
			self.out.addLayer(); self.endline()
			ann_endline = self.out.popLayer()
			
			# another annotation, means that this one is probably a group/subgroup
			if self.match_value('@'): self.out.annotation(annotation, ann_params, None, ann_endline)
		
		# member : [[static]? var|const] variable_name [: [type]? ]? = expression
		if ( constant := self.expect('const') ) or self.expect('var'):
			memberName = self.consume()

			if annotation: self.out.annotation(annotation, ann_params, memberName, ann_endline)

			self.declare( memberName, \
					 self.DECL_FLAGS.property \
				| (  self.DECL_FLAGS.constant if constant \
				else self.DECL_FLAGS.static if static \
				else self.DECL_FLAGS.onready if onready \
				else self.DECL_FLAGS.none))
			
			
	
	
	# Method -> func <name>(*<params>) [-> <type>]? :[Block]
	def method(self, static):
		name = self.consume()
		self.expect('(')
		
		params, params_init = self.parseParamDefinition()
		
		# add params to locals
		for k,v in params.items(): self.locals[k] = v
		
		returnType = self.parseType() if self.expect('->') else None
		
		self.expect(':')
		
		# make transpiler write to a buffer
		# so we can parser block code, emit declaration then emit block code
		self.out.addLayer()
		blockType = self.Block()
		code = self.out.popLayer()
		
		returnType = returnType or blockType
		self.getClass().methods[name] = returnType
		override = not static and name in self.getClassParent().methods
		
		self.out.define_method(name, params, params_init, returnType, code, static, override)
	
	
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
	
	def signal(self):
		name = self.consume()
		self.getClass().members[name] = toSignalType(name)
		params = {}
		
		# TODO: check if signal params can have initializers
		if self.expect('('): params, _ = self.parseParamDefinition()
		
		self.out.define_signal(name, params)
	
	
	def statement(self):
		if   self.expect('pass'): return
		elif self.expect('var'): return self.declare(flags=self.DECL_FLAGS.none) or self.out.end_statement()
		elif self.expect('const'): return self.declare(flags=self.DECL_FLAGS.constant) or self.out.end_statement()
		elif self.expect('if'): return self.ifStmt()
		elif self.expect('while'): return self.whileStmt()
		elif self.expect('for'): return self.forStmt()
		elif self.expect('match'): return self.matchStmt()
		elif self.expect('return'):return self.returnStmt()
		elif self.expect('await'): return self.awaitStmt()
		elif self.expect('break'): return self.out.breakStmt();
		elif self.expect('continue'): return self.out.continueStmt()
		elif not self.match_type('LINE_END', 'COMMENT', 'LONG_STRING'): return self.reassign()
		return
	
	def ifStmt(self):
		cond = self.boolean(); next(cond)
		self.out.ifStmt(cond)
		
		self.expect(':')
		type = self.Block()
		
		while self.expect('elif'):
			cond2 = self.boolean(); next(cond2)
			self.out.elifStmt(cond2)
			
			self.expect(':')
			eliftype = self.Block()
			type = type or eliftype
		
		if self.expect('else') and self.expect(':'):
			self.out.elseStmt()
			elsetype = self.Block()
			type = type or elsetype

		return type
	
	def whileStmt(self):
		cond = self.boolean(); next(cond)
		self.out.whileStmt(cond)
		
		self.expect(':')
		type = self.Block()
		
		return type
	
	def forStmt(self):
		name = self.consume()
		iterator_type = self.parseType() if self.expect(':') else None
		
		self.expect('in')
		
		exp = self.expression()
		exp_type = next(exp)

		inner_type = (exp_type.replace('[]', '') if exp_type and exp_type != 'Array' else 'Variant')
		iterator_type = iterator_type or inner_type
		
		self.locals[name] = iterator_type
		self.out.forStmt(name, iterator_type, exp)
		
		self.expect(':')
		type = self.Block()
		
		return type
	
	def matchStmt(self):
		
		switch_level = None
		return_type = None
		
		def evaluated():
			nonlocal switch_level
			expr = self.expression()
			type = next(expr)
			yield type
			next(expr)
			self.expect(':')
			self.level += 1
			switch_level = self.level
			yield
		
		def cases():
			nonlocal return_type
			for _ in self.doWhile(lambda:self.level >= switch_level):
				self.endline()
				default = self.expect('_')
				pattern = 'default' if default else self.expression()
				if not default: next(pattern)
				whenExpr = self.boolean() if self.expect('when') else None
				if whenExpr: next(whenExpr)
				self.expect(':')
				self.out.addLayer()
				blockType = self.Block()
				code = self.out.popLayer()
				yield pattern, whenExpr, code
				return_type = return_type or blockType
		
		self.out.matchStmt(evaluated(), cases)
		
		return return_type
	
	def returnStmt(self):
		exp = self.expression()
		type = next(exp)
		self.out.returnStmt(exp)
		self.out.end_statement()
		return type
	
	def awaitStmt(self):
		# NOTE: not that portable
		# but c++ has no equivalent anyway afaik
		self.out.addLayer()
		exp = self.expression(); next(exp); next(exp)
		exp_str = self.out.popLayer()
		splitExpr = exp_str.rsplit('.', 1)
		object = splitExpr[0] if len(splitExpr) > 1 else 'self'
		signalName = splitExpr[-1]
		self.out.awaitStmt(object, signalName)
		
	
	def declare(self, name = None, flags = DECL_FLAGS.none):
		if not name: name = self.consume()
		
		# could be a setget colon
		foundColon  = self.expect(':')
		foundSetGet = foundColon and not self.match_type('TEXT', '=')
		type = self.parseType() if foundColon and self.match_type('TEXT') else None
		
		# parsing assignment if needed
		ass = None
		if self.expect('='):
			ass = self.expression()
			ass_type = next(ass)
			type = type or ass_type
		
		type = type or 'Variant'
		
		# emit code
		if not flags & self.DECL_FLAGS.property:
			self.locals[name] = type
			self.out.declare_variable(type, name, ass)

		else:
			self.getClass().members[name] = type

			def emit(setget):
				self.out.declare_property(type, name, ass, \
					setget, \
					flags & self.DECL_FLAGS.constant, \
					flags & self.DECL_FLAGS.static, \
					flags & self.DECL_FLAGS.onready)
			
			if not (self.expect(':') or foundSetGet):
				emit(None)
				self.out.end_statement()
				
			# setget -> : [get [= <method_name>]|[ : Block ]]?, [set [= <method_name>]|[ : Block ]]?
			else:
				# although scope is used in C# to delimit getters and setters,
				# c++ does not have that notion
				# so we don't emit UpScope and DownScope here
				if self.match_type('COMMENT'): self.out +=' '; self.out.comment(self.consume())
				self.expect_type('LINE_END')
				
				oldLevel = self.level
				self.level += 1
				
				def impl():
					# allow defining setter and getter in any order
					for i in range(2):
						
						if self.expect('get'):
							if self.expect('='):
								yield 'getter_method', self.consume()
							
							elif self.expect(':'):
								self.out.addLayer()
								self.Block()
								code = self.out.popLayer()
								yield 'getter', code
						
						elif self.expect('set'):
							if self.expect('='):
								yield 'setter_method', self.consume()
							
							elif self.expect('('):
								valueName = self.consume(); self.expect(')', ':')
								self.out.addLayer()
								self.Block()
								code = self.out.popLayer()
								yield 'setter', valueName, code
						
						self.expect(',')
				
				emit(impl())
				self.level = oldLevel
	
	
	# reassign : <expression> =|+=!*=!... <expression>
	def reassign(self):
		# NOTE: expression() handles function calls and modification operators (a += b)
		# even though it is not conceptually correct
		exp = self.expression(); next(exp)
		if self.expect('='):
			self.endline()
			ass = self.expression(); next(ass)
			next(exp); self.out.assignment(ass)
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
	dereference		-> value [reference|subscription]?
	value			-> literal|subexpression|variable[call]?
	literal			-> int|float|string|array|dict
	array			-> [ [expresssion [, expression]*]? ]
	dict			-> { [expresssion:expression [, expresssion:expression]*]? }
	subexpression	-> (expression)
	variable		-> <name>
	reference		-> .name [reference|call|subscription]?
	call			-> ([params]*) [reference|subscription]?
	subscription	-> [expression] [reference|call|subscription]?
	
	"""	
	
	def expression(self):
		exp = self.ternary()
		type = next(exp)
		# NOTE: type casting will work in C# with a as keyword, but wont with c++
		# TBD if we need to do something here
		if self.expect('as'): type = self.parseType()
		yield type
		next(exp)
		yield
	
	def ternary(self):
		valTrue = self.boolean()
		valTrue_type = next(valTrue)
		if self.expect('if'):
			cond = self.boolean(); next(cond)
			self.expect('else')
			valFalse = self.ternary()
			valFalse_type = next(valFalse)
			yield valTrue_type or valFalse_type
			self.out.ternary(cond, valTrue, valFalse)
		else:
			yield valTrue_type
			next(valTrue)
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
			
		# handling type checks here
		elif self.expect('is'):
			checked = self.parseType()
			yield 'bool'
			self.out.check_type(ar1, checked)

		# handling "<element> in <array>" checks
		elif (negative := self.expect('not')) or self.expect('in'):
			finished = self.expect('in')
			if negative and not finished: print("unexpected 'not' :  ", self.current)
			val = self.expression()
			val_type = next(val)
			yield 'bool'
			if negative: self.out.operator('not')
			next(val)
			self.out.reference('', ar_type, val_type)
			self.out.call('Array', 'has', (ar1,))
		
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
		val1 = self.dereference()
		type = next(val1)

		self.subexpression_endline()
		
		# NOTE: we accept arithmetic reassignment ex: i -= 1
		# which is not exact but simpler to do this way
		op = self.consume() if self.match_type('ARITHMETIC') else None
		
		if op:
			val2 = self._arithmetic()
			type = next(val2)
			yield type
			next(val1)
			self.out.operator(op)
			next(val2)
		else:
			yield type
			next(val1)
		yield
	

	def dereference(self):
		val = self.value()
		type = next(val)

		signal = type and type.endswith('signal')
		singleton = type and type.endswith('singleton')
		if singleton: type = type[:-len('singleton')]
		
		# reference
		if self.expect('.'):
			ref = self.reference(type, singleton)
			yield next(ref)
			if not signal: next(val)
			next(ref)
		
		# subscription
		elif self.expect('['):
			sub = self.subscription(type)
			yield next(sub)
			next(val); next(sub)

		# no dereferencing
		else:
			yield type
			next(val)

		yield



	def value(self):

		self.subexpression_endline()
		
		# int and hexadecimals are supported as-is by cpp and C#
		if self.match_type('INT') or self.match_type('HEX'):
			val = self.consume()
			yield 'int'
			self.out.literal(val)
			
		# float
		elif self.match_type('FLOAT'):
			val = float(self.consume())
			yield 'float'
			self.out.literal(val)
			
		# bool
		elif self.match_value('true', 'false'):
			val = self.consume() == 'true'
			yield 'bool'
			self.out.literal(val)
		
		# multiline (""") string
		elif self.match_type('LONG_STRING'):
			val = self.consume()
			yield 'string'
			self.out.string(val)

		# "" or '' string
		elif self.match_type('STRING'):
			val = self.consume()
			yield 'string'
			self.out.string(val)
		
		# NOTE: we try to keep indentation
		# but pbbly better to just use a layer

		# array
		elif self.expect('['):
			self.out.level += 1 # for cpp to keep indentation
			self.out.addLayer(); self.endline()
			for val in self.doWhile(lambda: not self.expect(']')):
				val = self.expression(); next(val)
				self.out.array_item(val)
				self.expect(','); self.endline()
			contents = self.out.popLayer()
			self.out.level -= 1
			yield 'Array'
			self.out.create_array(contents)
			
		# dictionary
		elif self.expect('{'):
			self.out.level += 1 # for cpp to keep indentation
			self.out.addLayer(); self.endline()
			for _ in self.doWhile(lambda: not self.expect('}')):
				key = self.expression(); val = self.expression()
				next(key); self.expect(':'); next(val)
				self.out.dict_item(key, val)
				self.expect(','); self.endline()
			contents = self.out.popLayer()
			self.out.level -= 1
			yield 'Dictionary'
			self.out.create_dict(contents)
			
		# subexpression : (expression)
		elif self.expect('('):
			sub_subexpression = self.in_subexpression
			self.in_subexpression = True
			self.endline()
			enclosed = self.expression()
			enclosed_type = next(enclosed)
			self.endline()
			self.expect(')')
			if not sub_subexpression:
				self.in_subexpression = False
			yield enclosed_type
			self.out.subexpression(enclosed)
		
		# get_node shortcuts : $node => get_node("node") -> Node
		elif self.expect('$'):
			name = self.consume()
			yield 'Node'
			self.out.call('Node', 'get_node', (passthrough(self.out.string, name) ,) )
			
		# scene-unique nodes : %node => get_node("%node") -> Node
		elif self.expect('%'):
			name = self.consume()
			yield 'Node'
			self.out.call('Node', 'get_node', (passthrough(self.out.string, f'%{name}') ,) )
		
		# lambda: func <name>?(params): <Block>
		elif self.expect('func'):
			name = self.consume() if self.match_type('TEXT') else None
			self.expect('(')
			params, _ = self.parseParamDefinition()
			self.expect(':')
			self.expect_type('LINE_END')
			self.out.addLayer()
			_ret_type_ = self.Block()
			code = self.out.popLayer()
			# NOTE: we could use block's type inference
			# but then we'd need special code for when lambda is called
			yield 'Callable'
			self.out.create_lambda(params, code)
		
		# variable name
		elif self.match_type('TEXT'):
		
			name = self.consume()
			
			# self. is essentially just syntactic in most languages
			#this = name == 'self' and self.expect('.')
			#if this: name = self.consume()
			
			# call
			if self.expect('('):
				call = self.call(name)
				yield next(call)
				next(call)
			
			# variable
			else:
				# could be :
				# a member (including signals)
				# a local
				# a singleton or constructor (ex: RenderingServer, Vector3)
				# a global constant (ex: KEY_ESCAPE)
				singleton = name in godot_types[GLOBALS].members
				# NOTE: a case could be made to use getters on parent properties
				# I personnaly think you should store the parent property value then set it later
				# so leaving as-is
				parent_property = name in self.getClassParent().members
				property = name in self.getClass().members or parent_property
				enum = name + 'enum' in self.getClass().enums.values()

				type = self.getClass().members.get(name) \
					or self.getClassParent().members.get(name) \
					or self.locals.get(name) \
					or self.getClass().constants.get(name) \
					or godot_types[GLOBALS].constants.get(name) \
					or self.getClass().enums.get(name) \
					or (self.getClassName() if name == 'self' or enum else None) \
					or (name if singleton or name in godot_types else None)

				if singleton: type += 'singleton'

				yield type

				if singleton:  self.out.singleton(name)
				elif property: self.out.property(name)
				else:          self.out.variable(name)

		else: yield
		yield


	def referencesCallsAndSubscriptions(self, from_type = None):
		# reference
		if self.expect('.'):
			ref = self.reference(from_type)
			yield next(ref)
			next(ref)
		
		# call
		elif self.expect('('):
			call = self.call('', from_type)
			yield next(call)
			next(call)

		# subscription
		elif self.expect('['):
			sub = self.subscription(from_type)
			yield next(sub)
			next(sub)
		
		# end
		else:
			yield from_type
		yield

	
	def subscription(self, type):
		if type:
			type = (type[:-2] if type.endswith('[]')
			  else type[type.index(',')+1:-1] if type.startswith('Dictionary<')
			  else None)
		key = self.expression(); next(key)
		self.expect(']')
		
		# in case the expression continues
		follows = self.referencesCallsAndSubscriptions(type)
		yield next(follows)

		self.out.subscription(key)

		next(follows)
		yield

	
	def call(self, name, calling_type = None):
		
		# could be :
		# a constructor
		# a local method
		# a global function
		# another class's method
		constructor = name in godot_types
		godot_method = calling_type and calling_type in godot_types
		global_function = not calling_type and name in godot_types[GLOBALS].methods
		type = (name if constructor else None ) \
			or self.getClass().methods.get(name) \
			or self.getClassParent().methods.get(name) \
			or (godot_types[calling_type].methods.get(name) if godot_method \
			else godot_types[GLOBALS].methods.get(name) if global_function \
			else None)
		
		params = ( *self.parseCallParams() ,)
		
		# in case the expression continues
		follows = self.referencesCallsAndSubscriptions(type)
		yield next(follows)

		if constructor: self.out.constructor(name, type, params)
		else: self.out.call(GLOBALS if global_function else calling_type, name, params)

		next(follows)
		yield
	
	
	# NOTE: having to handle signals, function names, enums and constants here makes this unwieldy
	def reference(self, type, singleton = False):
		name = self.consume()

		enum = type and godot_types.get(type) and name in godot_types[type].enums
		constant = type and godot_types.get(type) and name in godot_types[type].constants
		member_type = godot_types[type].members[name] \
			if type in godot_types and name in godot_types[type].members \
			else godot_types[type].enums[name] if enum \
			else godot_types[type].constants[name] if constant \
			else None
		signal = member_type and member_type.endswith('signal')

		def emit(silent = False):
			if signal or silent: self.out.reference('', type, member_type, singleton)
			else: self.out.reference(name, type, member_type, singleton)
		
		# signal emission/connection
		if type and type.endswith('signal'):
			signal_name = type.replace('signal', '')
			self.expect('('); params = ( *self.parseCallParams() ,)
			yield None
			if name == 'emit':
				self.out.emitSignal(signal_name, params)
			elif name == 'connect':
				self.out.connectSignal(signal_name, params)

		# call
		elif self.expect('('):
			call = self.call(name, type)
			yield next(call)
			emit(silent = True)
			next(call)
		
		# other reference
		elif self.expect('.'):
			r = self.reference(member_type, singleton)
			yield next(r)
			emit()
			next(r)
		
		# subscription
		elif self.expect('['):
			s = self.subscription(type)
			yield next(s)
			emit()
			next(s)

		# handling reassignment here (though not an expression)
		elif self.match_value('=') or (self.match_type('ARITHMETIC') and self.current.value.endswith('=')):
			op = self.consume()
			val = self.expression() 
			yield next(val)
			self.out.reassignment(name, type, member_type, singleton, op, val)
		
		# end leaf
		else:
			if enum and type:
				yield f'{type}.{member_type}'
			else: yield member_type

			if enum:
				if type and type != self.getClassName():
					self.out.constant(member_type[:-len('enum')])

			if enum or constant: self.out.constant(name)
			else: self.out.reference(name, type, member_type, singleton)
		yield
	
	
	""" utils """
	
	# using a stack to keep track of class being defined
	def add_class(self, class_name, base_class, is_main = False):
		self.classes.append(class_name)
		if class_name not in godot_types:
			classData = ClassData()
			classData.base = base_class
			godot_types[class_name] = classData
		
		self.emit_class_change()
		self.out.define_class(class_name, base_class, self.is_tool, is_main)
	
	def end_class(self):
		self.out.end_class(self.getClassName())
		if len(self.classes) > 1: self.classes.pop()
		self.emit_class_change()
	
	def getClassName(self): return  self.classes[-1]

	def emit_class_change(self):
		self.out.current_class(self.getClassName(), self.getClass())
	
	def getClass(self):
		return godot_types[self.getClassName()]
		
	def getClassParent(self):
		parent_name = godot_types[self.getClassName()].base
		parent = godot_types.get(parent_name) \
			or godot_types.get('Object')
		return parent
	
	# parse call params
	def parseCallParams(self):
		for _ in self.doWhile(lambda: not self.expect(')')):
			exp = self.expression(); next(exp); yield exp
			self.expect(','); self.endline()
	
	
	""" parsing """
	
	def advance(self):
		try:
			self.current = next(self.tokens)
		except StopIteration as err:
			# reached end of file
			# using a trick to finish parsing
			self.current = copy(self.current)
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
	
	def expect(self, *tokens):
		found = True
		for token in tokens:
			found = found and self.match_value(token)
			if found: self.advance()
			else: break
		return found
	
	def expect_type(self, token):
		found = self.match_type(token)
		if found: self.advance()
		return found
	
	def consume(self):
		found = self.current.value
		self.advance()
		self.vprint('consumed:', found)
		return found
	
	# parse type string and format it the way godot docs do
	def parseType(self):
		type = self.consume()

		# parser convention : 'void' is None
		# convert it for when someone uses the function return type annotation
		# Ex : ```func _ready() -> void: ``` 
		if type == 'void': return None

		while self.expect('.'): type += '.' + self.consume()

		# Array[type] => type[]
		if type == 'Array' and self.expect('['):
			type = self.parseType() + '[]'; self.expect(']')

		# Dictionary[type, type] => Dictionary<type, type>
		if type == 'Dictionary' and self.expect('['):
			keyType = self.parseType(); self.expect(',')
			valueType = self.parseType(); self.expect(']')
			type = f'Dictionary<{keyType},{valueType}>'

		return type
		
	def consumeUntil(self, token, separator = ''):
		result = []
		for _ in self.doWhile(lambda : \
					not self.match_value(token) \
				and not self.match_type(token)):
			result.append(self.consume())
		return separator.join(result)
	
	# parse params definition (call, signal, lambda)
	# NOTE: also used to parse enums
	def parseParamDefinition(self, closing_char = ')'):
		params = {}
		params_init = {}
		
		# param -> <name> [: [<type>]?]? [= <Expression>]?
		for _ in self.doWhile(lambda: not self.expect(closing_char)):

			# NOTE: ignoring endlines and comments
			if self.expect_type('LINE_END'): continue 
			# TODO: keep input formating  instead
			
			pName = self.consume()
			pType = self.parseType() if self.expect(':') and self.match_type('TEXT') else None
			
			# initialisation
			if self.expect('='):
				pInit = self.expression()
				initType = next(pInit)
				pType = pType or initType
				params_init[pName] = pInit
			
			pType = pType or 'Variant'
			self.expect(',')
			params[pName] = pType
		
		# NOTE: params_init only used in method definition
		return params, params_init
	
	def subexpression_endline(self):
		if self.in_subexpression: self.endline()

	# called when an endline is excpected
	def endline(self):
		lastendline = None
		jumpedLines = 0
		emitComment = None
		
		while True:

			# setting scope level only when we encounter non-whitespace
			if self.match_type('LINE_END'):
				lastendline = self.current
				self.advance()
				jumpedLines += 1

			# parse comments
			elif self.match_type('COMMENT', 'LONG_STRING'):
				if emitComment: emitComment()
				emit = self.out.comment if self.match_type('COMMENT') else self.out.multiline_comment
				content = self.consume()
				def emitComment():
					nonlocal jumpedLines
					if jumpedLines > 0: self.out += '\n' * jumpedLines 
					emit(content)
					self.out += '\n'
					jumpedLines = -1
			
			# found code, indentation now matters, and break loop
			# NOTE: for prettier output, we emit downscope directly
			else:
				lvl = int(lastendline.value) if lastendline else self.level
				for i in range(self.level - lvl): self.out.DownScope();
				if lvl < self.level: self.level = lvl
				if emitComment: emitComment()
				else: self.out += '\n' * jumpedLines
				break

def passthrough(closure, *values):
	closure(*values); yield
