import re
import os
import godotReference as ref


# recursive descent parser
class Parser:
	
	
	def __init__(self, filename, text, transpiler):
		# keep track of the script being transpiled
		self.script_name = filename
		# transpiler renamed 'out' for brevity
		self.out = transpiler
		
		# splitting text into tokens
		text = text.replace(' ' * 4, '\t') # 4 whitespaces = 1 tab
		# split into tokens (we consider non-words full tokens)
		self.tokens = re.split('(\W)', text)
		# ignore empty strings...
		self.tokens =  [token for token in self.tokens if token]
		
		# char index in original script
		self.index = 0
		# indentation level
		self.level = 0
		# line number in original script (starting at 0)
		self.line = 0
		# token index corresponding to line start
		self.line_index = 0
		
		# script class data
		self.is_tool = None
		self.base_class = None
		self.class_name = None
		self.data = ref.ClassData()
		
		# NOTES:
		# * tokens kept as strings to avoid adding 1k+ code
		# * it might be more memory-friendly to use re.finditer instead of re.split
		# 	so we have an iterator and not an array of tokens
	
	
	""" parsing utils """
	
	def current(self, n = 1):
		return ''.join(self.tokens[self.index:self.index+n]) if n>1 else self.tokens[self.index]
	
	def tkn_is_text(self):
		tkn0 = self.current()[0]
		return tkn0.isalpha() or tkn0 in '_'
	
	def tkn_is_int(self):
		return self.current().isdigit() and self.current(2)[-1] != '.'
	
	def tkn_is_float(self):
		currrent = self.current()
		next = self.tokens[self.index+1]
		return (currrent.isdigit() and next == '.') or (next.isdigit() and currrent == '.')
	
	def skip_whitespace(self):
		while self.current() in ' \r': self.index +=1
	
	def expect(self, token, n = 1):
		self.skip_whitespace()
		
		# fast fail : check first char
		current = self.current()
		token0 = token[0]
		current0 = current[0]
		if current0 != token0 : return False
		
		found = self.current(n)
		match = token == found
		
		if match and token == '\n':
			self.line += 1
			self.line_index = self.index
			#print('********** line')
		#elif found:
		#	print(f'{token} ? => {found}')
		
		if match: self.index+=n
		
		self.skip_whitespace()
		return match
	
	def consume(self, n = 1):
		if self.tokens[self.index] == '\n': print("an EOL has been consumed !", self.index)
		found = self.current(n)
		print('+', found)
		self.index+=n
		return found
	
	def consumeUntil(self, end, n = 1, keep_end = True, ignore = []):
		# storing index makes us keep spaces past the 1st token
		start = self.index
		while not self.current(n) == end: self.index += 1
		self.index += n
		range = self.tokens[start:self.index - (0 if keep_end else n)]
		if ignore: range = [item for item in range if item not in ignore]
		return ''.join(range)
	
	
	""" parsing / transpiling """
	
	def comments(self):
		if self.expect('#'):
			content = self.consumeUntil('\n')
			self.out.line_comment(content)
		elif self.expect('"""', 3):
			content = self.consumeUntil('"""', 3, keep_end=False)
			self.out.multiline_comment(content)
	
	# ignore 
	def endline(self):
		lvl = -1
		while True:
			# ignore comments
			self.comments()
			# setting scope level only when we encounter non-whitespace
			if not self.expect('\n'):
				# go up and down in scope
				# NOTE: we assume scope is managed the same way across languages
				if lvl != -1:
					while lvl > self.level: self.out.UpScope(); self.level +=1
					while lvl < self.level: self.out.DownScope(); self.level -=1
				return
			
			# add endline in generated code to match script
			self.out += '\n'
			
			# count indentation to determine scope level
			lvl = 0
			while self.expect('\t'): lvl +=1
	
	
	def transpile(self):
		
		# in case there is a file header / comments at start
		self.endline()
		
		# script start specific statements
		self.is_tool = self.expect('@tool', 2); self.endline()
		self.base_class = self.consume() if self.expect('extends') else 'Object'; self.endline()
		self.class_name = self.consume() if self.expect('class_name') else self.script_name
		
		# no endline after class name since we declare the class before that
		self.out.define_class(self.class_name, self.base_class, self.is_tool); self.endline()
		
		# script-level loop
		end = len(self.tokens)
		last_index = -1
		while self.index < end and self.index != last_index:
			last_index = self.index
			# script/class level statements
			self.class_body()
		# end script class
		self.out.DownScope()
		
		# tell the transpiler we're done
		self.out.end_script()
		
		preview = min(end-last_index, 5)
		print("stopping at", self.line, self.index - self.line_index, f'<{self.current(preview)}>')
	
	
	def class_body(self):
		# gdscript 4 accepts nested classes
		self.nested_class()
		# enum definition
		self.enum()
		# class member definition
		self.member()
		# end statement
		self.endline()
	
	
	def nested_class(self):
		if self.expect('class'):
			class_name = self.consume()
			base_class = self.consume() if self.expect('extends') else 'Object'
			# NOTE: can inner classes be tools ?
			# are they the same as their script class ?
			self.out.define_class(class_name, base_class, False)
			self.expect(':')
			
			self.level += 1
			class_lvl = self.level
			while self.level >= class_lvl:
				# NOTE: no annotations in inner classes
				self.class_body()
	
	# TODO: support enum as variable type, ex: "var v = MyEnum.FOO" => "MyEnum v = MyEnum.FOO;"
	# NOTE: enums have similar syntax in gdscript, C# and cpp
	# lazily passing the enum definition as-is for now
	def enum(self):
		if self.expect('enum'):
			name = self.consume() if self.tkn_is_text() else ''
			self.skip_whitespace()
			definition = self.consumeUntil('}', keep_end=True)
			self.out.enum(name, definition)
	
	# class member 
	def member(self):
		# NOTE: special case for onready (needs moving the assignment into ready function)
		# TODO: call out.assignement with onready flag (later)
		is_onready = self.expect('@onready')
		self.annotation()
		self.variable_declaration()
		# TODO: handle get set
	
	
	# exports and such : @annotation[(params)]?
	def annotation(self):
		if self.expect('@'):
			name = self.consume()
			# NOTE: this should work for most cases
			params = self.consumeUntil(')', keep_end=False, ignore=['"', "'"]) if self.expect('(') else ''
			self.out.annotation(name, params)
	
	
	# variable : [var|const] variable_name [: [type]? ]? = expression
	def variable_declaration(self):
		# NOTE: constants should only be declared at script/inner class level
		constant = self.expect('const') 
		static = self.expect('static') 
		if constant or self.expect('var'):
			name = self.consume()
			type = self.consume() if self.expect(':') and self.tkn_is_text() else None
			# discarding array content's type, for now
			if type == 'Array' and self.expect('['):
				# convert to the way docs specify an array type
				type = self.consume() + '[]'
				self.expect(']')
			assignment = self.assignment_value()
			expression_type = next(assignment)
			type = type or expression_type or 'Variant'
			self.data.members[name] = type
			self.out.declare_variable(type, name, constant, static)
			next(assignment)
			self.out.end_statement()
	
	
	def statement(self):
		self.expect('pass')
	
	
	
	# assignment and all expression use generator/passthrough for type inference
	# the format expected is :
	# yield <type>
	# <emit code>
	
	def assignment_value(self):
		if self.expect('='):
			expression = self.expression()
			yield next(expression)
			self.out.assignment()
			yield next(expression)
		# nothing found, return empties
		else: yield; yield
	
	## GRAMMAR
	
	# Script
	#  |->Block = [<Statement>|<Member>]1+
	
	# Member -> [@annotation[(*params)]?]? [const| [static]? var] <name> [:<type>]? [= Expression ] 
	
	# Statement
	#  |->NoOperation     -> pass
	#  |->Declaration     -> def <variable> = <Expression>										----> TODO
	#  |->IfStatement     -> if <boolean>: <Block> [elif <boolean> <Block>]* [else <Block>]?    ----> TODO
	#  |->WhileStatement  -> while <boolean>: <Block>                                           ----> TODO
	#  |->ForStatement    -> for <variable> in <Expression> | : <Block>                         ----> TODO
	#  |->MatchStatement  -> match <Expression>: [<Expression>:<Block>]1+                       ----> TODO
	#  |->Assignment      -> <variable> = <Expression>                                          ----> TODO
	#  |->ReturnStatement -> return <Expression>                                                ----> TODO
	#  |->Expression (see below)                                                                ----> TODO
	
	# Expression	-> ternary
	# ternary		-> [boolean [if boolean else boolean]* ]			----> TODO
	# boolean		-> comparison [and|or comparison]*                  ----> TODO
	# comparison	-> arithmetic [<|>|==|... arithmetic]?              ----> TODO
	# arithmetic	-> value [*|/|+|-|... value]*                       ----> TODO
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
		ret = self.value
		return ret()
	
	def value(self):
		
		# int
		if self.tkn_is_int():
			val = int(self.consume())
			yield 'int'
			self.out.literal(val)
			
		# float
		elif self.tkn_is_float():
			val = float(self.consumeUntil('.') + (self.consume() if self.tkn_is_int() else ''))
			yield 'float'
			self.out.literal(val)
			
		# bool
		elif self.current() in ('true', 'false'):
			val = self.consume() == 'true'
			yield 'bool'
			self.out.literal(val)
		
		# TODO: support multiline (""") string
		
		# "" string
		elif self.expect('"'):
			val = self.consumeUntil('"', keep_end = False)
			yield 'string'
			self.out.literal(val)
		# '' string
		elif self.expect("'"):
			val = self.consumeUntil("'", keep_end = False)
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
		elif self.tkn_is_text():
			content = self.textCode()
			yield next(content)
			next(content)
		
		yield; yield
	
	# textCode : variable|call|reference
	def textCode(self):
		 
		 # ignoring 'self.' for now
		self.expect('self.', 2)
		
		name = self.consume()
		
		# type could be a singleton (ex: RenderingServer) or a call to a static function
		singleton = name in ref.godot_types
		type = self.data.members.get(name, None) or (name if singleton else None)
		
		# call
		if self.expect('('):
			call = self.call(None, name)
			yield next(call)
			next(call)
		
		# reference
		elif self.expect('.'):
			reference = self.reference(type)
			yield next(reference)
			self.out.singleton(name) if singleton else self.out.variable(name)
			next(reference)
		
		# subscription
		elif self.expect('['):
			s = self.subscription(type)
			yield next(s)
			self.out.variable(name)
			next(s)
		
		# lone variable or global
		else:
			yield self.data.members.get(name, None)
			self.out.variable(name)
		yield
		
	def call(self, type, name):
		
		# determine return type
		constructor = name in ref.godot_types
		type = name if constructor \
			else self.methods[name] if name in self.data.methods \
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
			yield 'int'
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