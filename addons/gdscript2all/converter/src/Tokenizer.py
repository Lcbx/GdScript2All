from libs.sly import Lexer

class Tokenizer(Lexer):
	# token types
	tokens = { COMMENT, LINE_END, TEXT, ARROW, FLOAT, HEX, INT, STRING, LONG_STRING, UNARY, COMPARISON, ARITHMETIC }
	
	# can be found alone, type will be same as value
	# ex: Token( value = ',' type = ',', ...)
	literals = { '.', ':', '(', ')', '[', ']', '{', '}', '@', '$', '%', ',', '\\', '='}
	
	# ignore whitespace and carriage returns
	ignore = ' \r'
	
	# Token definitions
	ARROW = r'->'
	ARITHMETIC = r'(<<|>>|\*\*|\*|\+|-|\/|%|&|\^|\|){1}=?' # << >> ** + - / 5 & ^ | (optionally = at the end)

	@_(r'(==|!=|<=|>=|\|\||&&|<|>|and|or){1}\W') # == != <= >= || && < > and or
	def COMPARISON(self, t): t.value = t.value.strip(); return t # remove trailing space

	UNARY = r'(~|!|not){1}'
	
	TEXT = r'[a-zA-Z_][a-zA-Z0-9_]*'
	FLOAT = r'\d+[.](\d*)?|[.]\d+' # accept 1. or 1.5 or .5
	HEX = r'0[xX][0-9a-fA-F]+'
	INT = r'\d+'


	# expression broken to the next line
	@_(r'\\\n\t*') # \ then any number of tabs
	def ignore_line_break(self, t): self.update_lineno(t)
	
	@_(r'#.*') # '#' then everything until endline
	def COMMENT(self, t):
		# remove '#'
		t.value = t.value[1:]; return t
	
	@_(r'"""[\S\s]*?"""')
	def LONG_STRING(self, t):
		self.update_lineno(t);
		# remove both """s
		t.value = t.value[3:-3]; return t
	
	@_(r'".*?"(?<!\\")|\'.*?\'(?<!\\\')') # accept both '' "" strings
	def STRING(self, t):
		self.update_lineno(t)
		# remove "" and replace \" by "
		t.value = t.value[1:-1].replace('\\'+t.value[0], t.value[0])
		return t
	
	@_(r'\n\t*') # at endlines, count tabs for scope level
	def LINE_END(self, t): self.update_lineno(t); t.value = str(t.value.count('\t')); return t
	
	# UTILS
	
	def update_lineno(self, t): self.lineno += t.value.count('\n')
	
	def error(self, t): # report unknown char and continue
		value = t.value[0]
		if value != '\t': # sometimes people leave trailing tabs, dont fret on that
			print(f"Ignoring character '{t.value[0]}' line {t.lineno} column {t.index}")
		self.index += 1
