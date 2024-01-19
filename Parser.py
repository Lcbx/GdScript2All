import re
import godotReference as ref

class Parser:
	
	def __init__(self, text, transpiler):
		self.index = 0
		self.level = 0
		self.line = 0
		self.out = transpiler # renamed out for brevity
		# separation into tokens
		text = text.replace(' ' * 4, '\t') # 4 whitespaces = 1 tab
		self.tokens =  [ token for token in re.split('(\W)', text) if token not in ' \r']
	
	def current(self):
		return self.tokens[self.index]
	
	def expect(self, token, n = 1):
		found = ''.join(self.tokens[self.index:self.index+n]) if n>1 else self.tokens[self.index]
		match = token == found
		
		if match and token == '\n': 
			self.line += 1
			#print('#######################################')
		
		elif found and found not in ' \r\n':
			_found = found.replace('\n','EOL')
			_token = token.replace('\n','EOL')
			print(f'{_token} ? => {_found}')
		
		if match: self.index+=n
		
		return match
	
	def consume(self, n = 1):
		found = ''.join(self.tokens[self.index:self.index+n]) if n>1 else self.tokens[self.index]
		print('consumed', found)
		self.index+=n
		return found
	
	def comments(self):
		if self.expect('#'):
			while not self.expect('\n'): self.index +=1
		elif self.current() == '"' and self.expect('"""', 3):
			while not self.expect('"""', 3): self.index +=1
			print("HI")
	
	def newline(self):
		while True:
			lvl = 0
			while self.expect('\t'): lvl +=1
			self.comments()
			if not self.expect('\n'):
				return lvl
	
	""" transpiler-specific part"""
	
	def transpile(self):
		
		self.newline()
		is_tool = self.expect('@tool', 2)
		self.newline()
		base_class = self.consume() if self.expect('extends') else "Godot.Object"
		self.newline()
		class_name = self.consume() if self.expect('class_name') else os.path.basename(outname).split('.')[0]
		self.newline()
		
		self.out.define_class(class_name, base_class, is_tool)
		
		#print(self.line, self.current())
		
		# script-level
		end = len(self.tokens)
		last_index = -1
		while self.index < end and self.index != last_index:
			last_index = self.index
			
			# go up and down in scope (= indentation)
			lvl = self.newline()
			if lvl > self.level: self.out.UpScope()
			elif lvl < self.level: self.out.DownScope()
			self.level = lvl
			
			# annotations
			self.annotation()
		
			# member definition
			self.member()
			
		
		print(self.line, self.current())
	
	def annotation(self):
		if self.expect('@'):
			if expect('onready'):
				# TODO: call out.assignement with onready flag
				pass
			else:
				name = self.consume()
				if expect('('):
					params = ""
					while not expect(')'):
						params += self.consume() + " "
				self.out.annotation(name, params)
			
	def member(self):
		self.variable()
		# TODO: get set
	
	def variable(self):
		if self.expect('var'):
			name = self.consume()
			if self.expect(":"):
				pass
