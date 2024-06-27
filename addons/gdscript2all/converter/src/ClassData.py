# to make pickle work
class ClassData:
	def __init__(self):
		self.base = None	# base class name
		self.members = {} 	# {name:type}
		self.methods = {}	# {name:return_type}
		self.constants = {}	# {name:type}
		self.enums = {}		# {constant_name:enum_name}