import os
import sys

# small and fast serialization
from pickle import dump as save, load

# allow using scripts in src folder
sys.path.insert(0,'src')

# see ClassData.py
from ClassData import ClassData


SAVEFILE = 'src/godot_types.pickle'
RAW_DATA_FILE = 'extension_api.json'


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
	#print(variant_types)

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
	from json import load as parse
	
	with open(RAW_DATA_FILE) as f:
		data = parse(f)
	
	#print( [ klass['name'] for klass in data['classes'] ])
	
	for klass in data['builtin_classes'] + data['classes']:
		klass_name = klass['name']
		#print('*', klass_name)

		if klass_name in {'Nil', 'float', 'int', 'bool'}: continue 

		classd = ClassData()
		godot_types[klass_name] = classd

		classd.base = klass.get('inherits')
		#print('->', classd.base)

		if methods := klass.get('methods'):
			for meth in methods:
				meth_name = meth['name']
				#print(meth_name)
				if 'return_value' in meth:
					classd.methods[meth_name] = meth['return_value'].get('type')

		if signals := klass.get('signals'):
			for signal in signals:
				signal_name = signal['name']
				#print(signal_name)
				classd.members[signal_name] = toSignalType(signal_name)

		if properties := klass.get('properties'):
			for prop in properties:
				prop_name = prop['name']
				#print(prop_name)
				classd.members[prop_name] = prop['type']

		if constants := klass.get('constants'):
			for const in constants:
				const_name = const['name']
				const_val = const['value']
				#print(const_name, const_val)
				const_type = 'int' if isinstance(const_val, int) \
					else const_val.split('(')[0]
				#print(const_name, const_type)
				classd.constants[const_name] = const_type

		if enums := klass.get('enums'):
			for enum in enums:
				enum_name = enum['name']
				#print(enum_name)
				classd.enums.append(enum_name)

	for klass in data['builtin_class_member_offsets'][0]['classes']:
		klass_name = klass['name']
		#print('*', klass_name)

		classd = ClassData()
		godot_types[klass_name] = classd

		for member in klass['members']:
			member_name = member['member']
			member_type = 'int' if (meta := member['meta']).startswith('int') \
				else meta
			classd.members[member_name] = member_type


	globals = ClassData()
	godot_types['@GlobalScope'] = globals

	for function in data['utility_functions']:
		func_name = function['name']
		func_type = function.get('return_type')
		# NOTE: might be useful if we can handle the whole Math/Mathf thing in C#
		#func_cat = function.get('category')
		globals.methods[func_name] = func_type


	for enum in data['global_enums']:
		enum_name = enum['name']
		globals.enums.append(enum_name)

		# mainly for keeping variant_types
		for enum_value in enum['values']:
			globals.constants[enum_value['name']] = 'int'

	## adding Variant for convenience
	godot_types['Variant'] = ClassData()

	## adding builtin that aren't in doc
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

