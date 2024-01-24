import re
import os
import godotReference as ref


# recursive descent parser
class Parser:
	
	
	def __init__(self, filename, text, transpiler):
		self.script_name = filename
		# char index in original script
		self.index = 0
		# indentation level
		self.level = 0
		# line number in original script (starting at 0)
		self.line = 0
		# token index corresponding to line start
		self.line_index = 0
		# transpiler renamed 'out' for brevity
		self.out = transpiler
		
		# splitting text into tokens
		text = text.replace(' ' * 4, '\t') # 4 whitespaces = 1 tab
		# split into tokens (we consider non-words full tokens)
		self.tokens = re.split('(\W)', text)
		# ignore empty strings...
		self.tokens =  [token for token in self.tokens if token != '']
		
		# NOTES:
		# * tokens kept as strings to avoid adding 1k+ code
		# * it might be more memory-friendly to use re.finditer instead of re.split
		# 	so we have an iterator and not an array of tokens
	
	
	""" parsing utils """
	
	def current(self, n = 1):
		#print(n, self.tokens[self.index-1], self.tokens[self.index], self.tokens[self.index+1])
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
		elif found:
			print(f'{token} ? => {found}')
		
		if match: self.index+=n
		
		self.skip_whitespace()
		return match
	
	def consume(self, n = 1):
		if self.tokens[self.index] == '\n': print("an EOL has been consumed !", self.index)
		found = self.current(n)
		print('+', found)
		self.index+=n
		return found
	
	# NOTE: consumes the end token wihout adding it to the result
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
				# NOTE: we assume scope is managed the same way across languagesgit 
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
		
		# in case there is a file header (in comments)
		self.endline()
		
		# script start specific statements
		is_tool = self.expect('@tool', 2); self.endline()
		base_class = self.consume() if self.expect('extends') else 'Object'; self.endline()
		class_name = self.consume() if self.expect('class_name') else self.script_name
		# no endline after class name since we declare the class before that
		self.out.define_class(class_name, base_class, is_tool); self.endline()
		
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
			params = self.consumeUntil(')', keep_end=False, ignore=['"', "'"]) if self.expect('(') else ""
			self.out.annotation(name, params)
	
	
	# variable : [var|const] variable_name [: [type]? ]? = expression
	def variable_declaration(self):
		# NOTE: constants should only be declared at script/inner class level
		constant = self.expect('const') 
		if constant or self.expect('var'):
			name = self.consume()
			type = self.consume() if self.expect(':') and self.tkn_is_text() else ''
			# discarding array type, for now
			if type == 'Array' and self.expect('['): self.consume(); self.expect(']')
			assignment = self.assignment()
			type_ = next(assignment)
			type = type if type else type_ if type_ else 'Object'
			self.out.declare_variable(type, name, constant)
			next(assignment)
			self.out.end_statement()
	
	
	# assignment and all expression use generator/coroutine for type inference
	# the format expected is :
	# yield <type>
	# <emit code>
	# yield None
	
	def assignment(self):
		if self.expect('='):
			expression = self.expression()
			yield next(expression)
			self.out.assignment()
			yield next(expression)
		# nothing found, return empties
		else: yield ''; yield None
	
	def expression(self):
		# ternary : boolean [if boolean else boolean]*
		# boolean : comparison [and|or comparison]*
		# comparison : arithmetic [<|>|==|... arithmetic]?
		# arithmetic : value [*|/|+|-|... value]*
		# value : [(ternary)]?|literal|collection|function|method]
		# function : <function>([expression[, expression]*]?)
		# method : <variable>.<method>([expression[, expression]*]?)
		# collection : array, dict
		# array : \[ [expresssion [, expression]*]? \]
		# dict : { [expresssion:expression [, expresssion:expression]*]? }
		# literal : int|float|string
		return self.literal()
	
	def literal(self):
		if self.tkn_is_int():
			val = int(self.consume())
			yield 'int'
			self.out.literal(val)
		elif self.tkn_is_float():
			val = float(self.consumeUntil('.') + (self.consume() if self.tkn_is_int() else ''))
			yield 'float'
			self.out.literal(val)
		elif self.current() in ('true', 'false'):
			val = self.consume() == 'true'
			yield 'bool'
			self.out.literal(val)
		# nothing found, return empties
		else: yield ''
		yield None
	
	
	def statement(self):
		self.expect('pass')
