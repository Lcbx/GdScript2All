import re
import godotReference as ref

class Parser:
	
	
	def __init__(self, text, transpiler):
		# char index in original script
		self.index = 0
		# indentation level
		self.level = 0
		# line number in original script (starting at 0)
		self.line = 0
		# transpiler renamed out for brevity
		self.out = transpiler
		# separation into tokens (tokens kept as strings to avoid adding 1k+ code)
		text = text.replace(' ' * 4, '\t') # 4 whitespaces = 1 tab
		self.tokens =  [ token for token in re.split('(\W)', text) if token not in ' \r']
	
	""" parsing utils """
	
	def current(self):
		return self.tokens[self.index]
	
	def expect(self, token, n = 1):
		
		# fast fail : check first char
		first = token[0]
		current = self.current()
		if first != current[0]: return False
		
		found = ''.join(self.tokens[self.index:self.index+n]) if n>1 else current
		match = token == found
		
		if match and token == '\n': 
			self.line += 1
			self.out += self.out.newline()
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
	
	def consumeUntil(self, token, n = 1):
		# fast fail : check first char
		start = self.index
		while not self.expect(token, n): self.consume()
		return ' '.join(self.tokens[start:self.index-n])
	
	""" parsing / transpiling """
	
	def comments(self):
		if self.expect('#'):
			content = self.consumeUntil('\n')
			self.out.line_comment(content)
		elif self.expect('"""', 3):
			content = self.consumeUntil('"""', 3)
			self.out.multiline_comment(content)
	
	def endStatement(self):
		#print("new line")
		while True:
			lvl = 0
			# count indentation
			while self.expect('\t'): lvl +=1
			# ignore comments
			self.comments()
			# ignore empty lines
			if not self.expect('\n'):
				# go up and down in scope 
				if lvl > self.level: self.out.UpScope()
				elif lvl < self.level: self.out.DownScope()
				self.level = lvl
				return
	
	def transpile(self):
		
		self.endStatement()
		
		is_tool = self.expect('@tool', 2); self.endStatement()
		base_class = self.consume() if self.expect('extends') else "Godot.Object"; self.endStatement()
		class_name = self.consume() if self.expect('class_name') else os.path.basename(outname).split('.')[0]
		self.out.define_class(class_name, base_class, is_tool); # no endStatement (see while loop later)
		
		#print(self.line, self.current())
		
		# script-level
		end = len(self.tokens)
		last_index = -1
		while self.index < end and self.index != last_index:
			last_index = self.index
			
			# end previous statement
			self.endStatement()
			
			# member definition
			self.member()
			
		
		print(self.line, self.current())
	
	def member(self):
		
		# annotations
		
		# TODO: call out.assignement with onready flag (later)
		is_onready = self.expect('@onready')
		
		if self.expect('@'):
			name = self.consume()
			if expect('('):
				params = ""
				while not expect(')'):
					params += self.consume() + " "
			self.out.annotation(name, params)
		
		self.variable_declaration()
		
		# TODO: handle get set
	
	def variable_declaration(self):
		if self.expect('var'):
			name = self.consume()
			if self.expect(":"):
				pass
