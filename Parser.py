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
	
	def endline(self):
		found_EOL = False
		while True:
			lvl = 0
			# count indentation
			while self.expect('\t'): lvl +=1
			# ignore comments
			self.comments()
			# ignore empty lines
			if not self.expect('\n'):
				if found_EOL:
					# go up and down in scope
					# NOTE: we assume scope is managed the same way across languages
					if lvl > self.level: self.out.UpScope()
					elif lvl < self.level: self.out.DownScope()
					self.level = lvl
				return
			found_EOL = True
			self.out += '\n'
	
	
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
			type = self.consume() if self.expect(":") and self.tkn_is_text() else ''
			type_, definition = self.assignment()
			type = type if type else type_ if type_ else 'Object'
			self.out.declare_variable(type, name, constant)
			if definition:definition()
			self.out.end_statement()
	
	
	# assignement and all expression returns a tuple -> (type : str, effect:closure)
	
	# util
	def create_effect(self, type, value, transparisation):
		return (type, lambda:transparisation(type, value))
	
	def assignment(self):
		if self.expect('='):
			type, expression = self.expression()
			if not expression: return type, expression
			def effect():
				self.out.assignment()
				if expression: expression()
			return type, effect
		return '', None
	
	def expression(self):
		# ternary : boolean [[if boolean]1+ else boolean]?
		# boolean : comparison [and|or comparison]*
		# comparison : arithmetic [<|>|==|... arithmetic]?
		# arithmetic : literal [*|/|+|-|... literal]*
		# ternary : [(ternary)]?|int|float|string|array|dict]
		return self.literal()
	
	def literal(self):
		if self.tkn_is_int():
			val = int(self.consume())
			return self.create_effect(int, val, self.out.literal)
		elif self.tkn_is_float():
			val = float(self.consumeUntil('.') + (self.consume() if self.tkn_is_int() else ''))
			return self.create_effect(float, val, self.out.literal)
		elif self.current() in ('true', 'false'):
			val = self.consume() == 'true'
			return self.create_effect(bool, val, self.out.literal)
		return '', None
	
	
	def statement(self):
		self.expect('pass')
