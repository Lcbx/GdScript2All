import os
import sys

# small and fast serialization
from pickle import dump as save, load

# allow using scripts in src folder
sys.path.insert(0,'src')

# see ClassData.py
from ClassData import ClassData


SAVEFILE = 'src/godot_types.pickle'
DOC_FOLDER = 'classData'


# the data people we import in this script
# { 'class': ClassData }
godot_types = {}

# variant types (names)
variant_types = []

def _import_type_definitions_():
	global godot_types
	global variant_types
	
	# load class datas
	with open(SAVEFILE, 'rb') as f:
		godot_types = load(f)
	
	# get variant type enum Ex: TYPE_FLOAT, TYPE_VECTOR2, etc
	variant_types = [ cst for cst in godot_types['@GlobalScope'].constants.keys() if cst.startswith('TYPE_') and not cst.endswith('MAX')]
	
	# decompression/flattening :
	# add base class members to child class
	
	# create a sort key : parents at the top, children afterward
	type_items = list(godot_types.items())
	sortKey = {}
	for i in range(10):
		for name, data in type_items:
			#print(name, data.base)
			if not name in sortKey: sortKey[name] = 0
			if data.base:
				points = sortKey[name] + 1
				sortKey[data.base] = sortKey.get(data.base, 0) + points
	
	type_items.sort(key=lambda kv: sortKey[kv[0]])
	type_items.reverse()
	
	#print( *(f'{k} {v.base} {sortKey[k]}\n' for k,v in type_items ) )
	
	# assert parents are really before their children
	for childIndex, (type, data) in enumerate(type_items):
		if data.base and data.base in godot_types:
			parentIndex = next( j for j, kv in enumerate(type_items) if kv[0] == data.base )
			#print(data.base, parentIndex, childIndex, type)
			assert parentIndex < childIndex , 'parent after the child while processing type infos'
	
	# add the data from parent to child
	from copy import copy
	for type, data in type_items:
		if data.base:
			#print(type, data.base)
			parent = godot_types[data.base]
			for method in parent.methods: data.methods[method] = parent.methods[method]
			for member in parent.members: data.members[member] = parent.members[member]
			for const in parent.constants: data.constants[const] = parent.constants[const]

def _update_type_definitions_():
	
	# generate the pickle file
	from untangle import parse
	
	classDocPaths = [
		os.path.join(root, file)
		for root, dirs, files in os.walk(DOC_FOLDER)
		for file in files
		if os.path.splitext(file)[1] == '.xml'
	]
	
	#print(classDocPaths)
	
	for path in classDocPaths:
		
		klass = parse(path).class_
		klass_name = klass['name']
		
		# skip native types
		if klass_name in ['float', 'int', 'bool']: continue 
		
		data = ClassData()
		godot_types[klass_name] = data
		
		data.base = klass['inherits']
		
		if 'methods' in klass:
			for meth in klass.methods.method:
				meth_name = meth['name']
				data.methods[meth_name] = meth.return_['type'] if 'return_' in meth else None
		
		if 'members' in klass:
			for memb in klass.members.member:
				memb_name = memb['name']
				data.members[memb_name] = memb['type']
		
		# NOTE: some constants are part of an enum
		# the enum name is then contained in constant.enum property
		if 'constants' in klass:
			for cons in klass.constants.constant:
				cons_name = cons['name']
				cons_val = cons['value']
				# no type in docs, so best guess
				# int : -?\d+
				# contructor : <type>(params)
				# NOTE: currently there are no float or string
				cons_type = 'int' if cons_val.lstrip('-').isdigit() \
					else cons_val.split('(')[0]
				data.constants[cons_name] = cons_type
		
		if 'signals' in klass:
			for signal in klass.signals.signal:
				signalName = signal['name']
				data.members[signalName] = toSignalType(signalName)
	
	# adding builtin that aren't in doc
	add_function('range', 'int[]')
	add_function('load', 'Resource')
	add_function('preload', 'Resource')
	
	with open(SAVEFILE, 'wb+') as f:
		save(godot_types, f)

	print('updated godot type definitions')

def add_function(name, return_type):
	godot_types['@GlobalScope'].methods[name] = return_type

def toSignalType(signal_name): return f'{signal_name}signal'

# if import then load types
if __name__ != "__main__":
	_import_type_definitions_()

# else update the type pickle
else:
	_update_type_definitions_()

