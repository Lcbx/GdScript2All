from io import StringIO

class StringBuilder(StringIO):
	
	#def __init__(self):
	#	self.content = ''
	
	def __iadd__(self, txt):
		self.write(str(txt))
		#self.write(txt)
		return self
	
	#def __add__(self, txt):
	#	self.write(str(txt))
	#	return self.getvalue()
	
	def __str__(self):
		return self.getvalue()
		#return self.content
	
	#def write(self, txt):
	#	self.content += str(txt)
	#	return self