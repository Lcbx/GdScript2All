import re
import os
from copy import copy
from enum import IntFlag as Flags

from ClassData import ClassData
from godot_types import godot_types
from Tokenizer import Tokenizer


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
		self.tokens = self.tokenizer.tokenize(text)
		
		# update current token
		self.advance()
		
		# indentation level
		self.level = 0
		
		# script class data
		self.is_tool = None
		self.class_name = None
		
		# class names in order of definition in file
		self.classes = []
		
		# local class definitions (class_name:classData)
		self.class_definitions = {}
		
		# local variables (name:type)
		self.locals = {}
	
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
	 |->Assignment      -> <Expression> = <Expression>
	 |->Expression (see after statement implementation)
	
	Expression grammar defined later
	
	"""
	
	def transpile(self):
	
		# in case there is a file header / comments at start
		self.endline()
		
		# script start specific statements
		self.is_tool = self.expect('@', 'tool'); self.endline()
		base_class = self.consume() if self.expect('extends') else 'Object'; self.endline()
		class_name = self.consume() if self.expect('class_name') else self.script_name
		# NOTE: no endline after class name since we declare the class before that
		
		# initialize script class data
		self.add_class(class_name, base_class, self.is_tool); self.endline()
		
		# script-level loop
		for i in range(2):
			
			for _ in self.doWhile(lambda:True):
				self.class_body()
			
			# get out if EOF reached
			if self.match_type('EOF'): self.vprint("reached EOF"); break
			
			# panic system : drop current line if we can't parse it
			token = self.current
			escaped = self.consumeUntil('LINE_END', separator=' '); self.endline()
			# add comment to output + print red warning in console output
			msg = f'PANIC! <{escaped}> unexpected at {token}'
			self.out.comment(f'{msg}\n')
			print(f'\033[91m{msg}\033[0m')
		
		# tell the transpiler we're done
		self.out.end_script()
	
	
	def class_body(self):
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
		class_lvl = self.level
		for _ in self.doWhile(lambda:self.level >= class_lvl): self.class_body()
		
		self.end_class()
	
	
	def enum(self):
		# NOTE: enums have similar syntax in gdscript, C# and cpp
		# lazily passing the enum definition as-is for now
		name = self.consume() if self.match_type('TEXT') else ''
		definition = self.consumeUntil('}')
		definition += self.consume() # get the remaining '}'
		self.out.enum(name, definition)
	
	
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
			if self.expect('onready'): onready = True; self.endline(); break
			
			annotation = self.consume()
			# NOTE: this should work for most cases
			if self.expect('('): ann_params = self.consumeUntil(')').replace('"', '').replace("'", ''); self.expect(')')
			else: ann_params = ''
			
			self.out.addLayer(); self.endline()
			ann_endline = self.out.popLayer()
			if not ann_endline: ann_endline = ' '
			
			# another annotation, means that this one is probably a group/subgroup
			if self.match_value('@'): self.out.annotation(annotation, ann_params); self.out.write(ann_endline)
		
		# member : [[static]? var|const] variable_name [: [type]? ]? = expression
		constant = self.expect('const')
		if constant or self.expect('var'):
			memberName = self.consume()
			if annotation: self.out.annotation(annotation, ann_params, memberName); self.out.write(ann_endline)
			foundSetGet = self.declare( memberName, \
					 self.DECL_FLAGS.property \
				| (  self.DECL_FLAGS.constant if constant \
				else self.DECL_FLAGS.static if static \
				else self.DECL_FLAGS.onready if onready \
				else self.DECL_FLAGS.none))
			
			if not (self.expect(':') or foundSetGet):
				self.out.end_statement()
				
			# setget -> : [get [= <method_name>]|[ : Block ]]?, [set [= <method_name>]|[ : Block ]]?
			else:
				# although scope is used in C# to delimit getters and setters,
				# c++ does not have that notion
				# so we don't emit UpScope and DownScope here
				if self.match_type('COMMENT'):
					self.out +=' '; self.out.comment(self.consume())
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
				
				self.out.setget(memberName, impl())
				self.level = oldLevel
	
	
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
	
	
	def Block(self, addBreak = False):
		self.level += 1
		block_lvl = self.level
		return_type = None
		
		self.out.UpScope()
		
		for _ in self.doWhile(lambda : self.level >= block_lvl):
			res = self.statement()
			return_type = return_type or res
			self.endline(addBreak = addBreak)
		
		return return_type
	
	def signal(self):
		name = self.consume()
		self.getClass().members[name] = f'signal/{name}'
		params = {}
		
		# TODO: check if signal params can have initializers
		if self.expect('('):
			params, _ = self.parseParamDefinition()
		
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
		
		self.expect('in')
		
		exp = self.expression()
		exp_type = next(exp)
		iterator_type = exp_type.replace('[]', '')
		
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
			yield type
		
		def cases(addBreak):
			nonlocal return_type
			for _ in self.doWhile(lambda:self.level >= switch_level):
				self.endline()
				default = self.expect('_')
				pattern = 'default' if default else self.expression()
				if not default: next(pattern)
				whenExpr = self.boolean() if self.expect('when') else None
				if whenExpr: next(whenExpr)
				self.expect(':')
				yield pattern, whenExpr
				blockType = self.Block(addBreak)
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
		splitExpr = self.out.popLayer().rsplit('.', 1)
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
			ass = self.assignment( name if flags & self.DECL_FLAGS.onready else None )
			ass_type = next(ass)
			type = type or ass_type
		
		type = type or 'Variant'
		
		# emit code
		if flags & self.DECL_FLAGS.property:
			self.getClass().members[name] = type
			self.out.declare_property(type, name, ass, \
				flags & self.DECL_FLAGS.constant, \
				flags & self.DECL_FLAGS.static)
		else:
			self.locals[name] = type
			self.out.declare_variable(type, name, ass)
		
		return foundSetGet
	
	
	# reassign : <expression> = <expression>
	def reassign(self):
		# NOTE: expression() handles function calls and modification operators (a += b)
		# even though it is not conceptually correct
		exp = self.expression()
		exists = next(exp)
		
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
		yield next(valTrue)
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
				self.endline(emitDownScope = False)
				for _ in self.doWhile(lambda: not self.expect(']')):
					val = self.expression(); next(val)
					self.expect(','); self.endline(emitDownScope = False)
					yield val
			self.out.create_array(iter())
			
		# dictionary
		elif self.expect('{'):
			yield 'Dictionary'
			def iter():
				self.endline(emitDownScope = False)
				for _ in self.doWhile(lambda: not self.expect('}')):
					key = self.expression(); val = self.expression()
					next(key); self.expect(':'); next(val)
					yield (key, val)
					self.expect(','); self.endline(emitDownScope = False)
			self.out.create_dict(iter())
			
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
		
		# could be :
		# a member (including signals)
		# a local
		# a singleton (ex: RenderingServer)
		# a global constant (ex: KEY_ESCAPE)
		singleton = name in godot_types
		property = name in self.getClass().members or name in self.getClassParent().members
		type = self.getClass().members.get(name) \
			or self.getClassParent().members.get(name) \
			or self.locals.get(name) \
			or godot_types['@GlobalScope'].constants.get(name) \
			or (name if singleton else None)
		signal = type and type.startswith('signal')
		
		emit = self.out.singleton if singleton \
			else self.out.property if property \
			else self.out.variable
		
		# call
		if self.expect('('):
			call = self.call(name)
			yield next(call)
			if this: self.out.this()
			next(call)
		
		# reference
		elif self.expect('.'):
			reference = self.reference(type)
			yield next(reference)
			if this: self.out.this()
			if not signal: emit(name)
			next(reference)
		
		# subscription
		elif self.expect('['):
			s = self.subscription(type)
			yield next(s)
			if this: self.out.this()
			emit(name)
			next(s)
		
		# lone variable or global
		else:
			yield type
			if this: self.out.this()
			emit(name)
		yield
	
	
	def call(self, name, calling_type = None):
		
		# could be :
		# a constructor
		# a local method
		# a global function
		# another class's method
		constructor = name in godot_types
		godot_method = calling_type and calling_type in godot_types
		global_function = not calling_type and name in godot_types['@GlobalScope'].methods
		type = (name if constructor else None ) \
			or self.getClass().methods.get(name) \
			or self.getClassParent().methods.get(name) \
			or (godot_types[calling_type].methods.get(name) if godot_method \
			else godot_types['@GlobalScope'].methods.get(name) if global_function \
			else None)
		
		params = ( *self.parseCallParams() ,)
		
		# emission of code 
		emit = lambda : \
			self.out.constructor(name, params) if constructor \
			else self.out.call(name, params, global_function)
		
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
		# TODO: take classes defined locally into account
		member_type = godot_types[type].members[name] if \
				type in godot_types and name in godot_types[type].members \
			else None
		signal = member_type and member_type.startswith('signal')
		
		# signal emission/ connection
		if type and type.startswith('signal'):
			signal_name = type.split('/')[-1]
			# determine params (same as call)
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
			# emit '.' while call() emits <name>(...)
			self.out.reference('')
			next(call)
		
		# other reference
		elif self.expect('.'):
			r = self.reference(member_type)
			yield next(r)
			if not signal:
				self.out.reference(name)
			else:
				# emit '.', next reference will be connect or emit
				self.out.reference('')
			next(r)
		
		# subscription
		elif self.expect('['):
			s = self.subscription(type)
			yield next(s)
			self.out.reference(name)
			next(s)
		
		# could be a constant
		elif type and name in godot_types[type].constants:
			yield godot_types[type].constants[name]
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
			call = self.call('', type)
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
	
	
	""" utils """
	
	# using a stack to keep track of class being defined
	def add_class(self, class_name, base_class, is_tool = False):
		self.classes.append(class_name)
		classData = ClassData()
		classData.base = base_class
		self.class_definitions[class_name] = classData
		
		self.emit_class_change()
		self.out.define_class(class_name, base_class, self.is_tool)
	
	def end_class(self):
		self.out.end_class(self.classes[-1])
		if len(self.classes) > 1: self.classes.pop()
		self.emit_class_change()
	
	def emit_class_change(self):
		self.out.current_class(self.classes[-1], self.getClass())
	
	def getClass(self):
		return self.class_definitions[self.classes[-1]]
		
	def getClassParent(self):
		class_name = self.classes[-1]
		parent_name = self.class_definitions[class_name].base
		parent = self.class_definitions.get(parent_name) \
			or godot_types.get(parent_name) \
			or godot_types.get('Object')
		return parent
	
	# parse call params
	def parseCallParams(self):
		while not self.expect(')'):
			exp = self.expression(); next(exp); yield exp
			self.expect(',')
	
	
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
		self.vprint('+', found)
		return found
	
	# parse type string and format it the way godot docs do
	def parseType(self):
		type = self.consume()
		# Array[<type>] => <type>[]
		if type == 'Array' and self.expect('['):
			type = self.consume() + '[]'; self.expect(']')
		return type
		
	def consumeUntil(self, token, separator = ''):
		result = []
		for _ in self.doWhile(lambda : \
					not self.match_value(token) \
				and not self.match_type(token)):
			result.append(self.consume())
		return separator.join(result)
	
	# parse params definition (call, signal, lambda)
	def parseParamDefinition(self):
		
		params = {}
		params_init = {}
		
		# param -> <name> [: [<type>]?]? [= <Expression>]?
		for _ in self.doWhile(lambda: not self.expect(')')):
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
	
	# called when an endline is excpected
	# addBreak is for switch statements
	def endline(self, emitDownScope = True, addBreak = False):
		jumpedLines = 0
		lastendline = None
		
		while self.match_type('LINE_END', 'COMMENT', 'LONG_STRING'):

			# stub
			emitComments = (lambda : None)

			# setting scope level only when we encounter non-whitespace
			if self.match_type('LINE_END'):
				lastendline = self.current
				self.advance()
				jumpedLines += 1

			# parse comments
			else:
				emit = self.out.comment if self.match_type('COMMENT') else self.out.multiline_comment
				content = self.consume()
				# override emitComments stub
				def emitComments(): emit(content)

			if self.match_type('LINE_END'):
				emitComments()
			
			# found code, indentation now matters
			# NOTE: for prettier output, we emit downscope directly
			else:
				if lastendline:
					lvl = int(lastendline.value)
					while lvl < self.level:
						if addBreak: self.out += '\n'; self.out.breakStmt(); addBreak =  False
						self.level -=1
						if emitDownScope: self.out.DownScope();
						#self.out += f"      <downscope {self.current}>"
				emitComments()
				self.out += '\n' * jumpedLines
				jumpedLines = 0

def passthrough(closure, *values):
	closure(*values); yield
