from io import StringIO

class StringBuilder(StringIO):
	
	def __iadd__(self, txt):
		self.write(str(txt))
		return self
	
	def __str__(self):
		return self.getvalue()