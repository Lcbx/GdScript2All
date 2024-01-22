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
		# separation into tokens (tokens kept as strings to avoid adding 1k+ code)
		text = text.replace(' ' * 4, '\t') # 4 whitespaces = 1 tab
		self.tokens =  [token for token in re.split('(\W)', text) if token != ''] # empty strings...
	
	""" parsing utils """
	
	def current(self, n = 1):
		#print(n, self.tokens[self.index-1], self.tokens[self.index], self.tokens[self.index+1])
		return ''.join(self.tokens[self.index:self.index+n]) if n>1 else self.tokens[self.index]
	
	def tkn_is_text(self):
		return self.current()[0].isalpha()
	
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
	def consumeUntil(self, end, n = 1, ignore = []):
		# storing index makes us keep spaces past the 1st token
		start = self.index
		while not self.expect(end, n): self.index += 1
		range = self.tokens[start:self.index-n]
		if ignore: range = [item for item in range if item not in ignore]
		return ''.join(range)
	
	
	
	""" parsing / transpiling """
	
	def comments(self):
		if self.expect('#'):
			content = self.consumeUntil('\n')
			self.out.line_comment(f'{content}\n')
		elif self.expect('"""', 3):
			content = self.consumeUntil('"""', 3)
			self.out.multiline_comment(content)
	
	def endline(self):
		while True:
			lvl = 0
			# count indentation
			while self.expect('\t'): lvl +=1
			# ignore comments
			self.comments()
			# ignore empty lines
			if not self.expect('\n'):
				# go up and down in scope
				# NOTE: we assume scope is managed the same way across languages
				if lvl > self.level: self.out.UpScope()
				elif lvl < self.level: self.out.DownScope()
				self.level = lvl
				return
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
			
			# class level statements
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
			# TODO: can inner classes be tools ?
			self.out.define_class(class_name, base_class, False)
			self.expect(':')
			
			self.level += 1
			class_lvl = self.level
			while self.level >= class_lvl:
				# NOTE: no annotations in inner classes
				self.class_body()
	
	
	def enum(self):
		if self.expect('enum'):
			name = consume() if self.tkn_is_text() else ''
			# TODO: {}
	
	
	# class member 
	def member(self):
		
		# NOTE: special case for onready
		# to make handling it easier (moving the assignment into ready function)
		is_onready = self.expect('@onready')
		# TODO: call out.assignement with onready flag (later)
		
		self.annotation()
		# NOTE: used in statements too
		self.variable_declaration()
		
		# TODO: handle get set
	
	
	# exports and such : @annotation[(params)]?
	def annotation(self):
		if self.expect('@'):
			name = self.consume()
			# NOTE: this should work for most cases
			params = self.consumeUntil(')', ignore=['"', "'"]) if self.expect('(') else ""
			self.out.annotation(name, params)
	
	
	# variable : [var|const] variable_name [: [type]? ]? = expression
	def variable_declaration(self):
		# NOTE: constants should only be declared at script/inner class level
		constant = self.expect('const') 
		if constant or self.expect('var'):
			name = self.consume()
			if self.expect(":"):
				if self.tkn_is_text():
					type = self.consume()
					print(f"declaring var", name, type)
	
	def statement(self):
		self.expect('pass')
