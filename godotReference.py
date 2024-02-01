import os
from untangle import parse
from pprint import pprint

class ClassData:
	def __init__(self):
		self.members = {} 	# {name:type}
		self.methods = {}	# {name:return_type}
		self.constants = []	# [name]

# { 'class': ClassData }
godot_types = {}

docFolder = 'GodotAPI'
classDocPaths = [
	os.path.join(root, file)
	for root, dirs, files in os.walk(docFolder)
	for file in files
	if os.path.splitext(file)[1] == '.xml'
]

for path in classDocPaths:
	
	# ignore globals for now
	if '@GlobalScope' in path: continue
	
	klass = parse(path).class_
	klass_name = klass['name']
	
	# skip native types
	if klass_name in ['float', 'int', 'bool']: continue 
	
	data = ClassData()
	godot_types[klass_name] = data
	
	if 'methods' in klass:
		for meth in klass.methods.method:
			meth_name = meth['name']
			data.methods[meth_name] = meth.return_['type']
	
	if 'members' in klass:
		for memb in klass.members.member:
			memb_name = memb['name']
			data.members[memb_name] = memb['type']
	
	if 'constants' in klass:
		for cons in klass.constants.constant:
			data.constants.append(cons['name'])

#pprint(godot_types)
#pprint(dir(godot_types["RenderingServer"]))


# TODO: support global scope functions
# TODO: save godot_types as json and load them directly ?
# TODO: separate godot API reference from C#-specific translation


# Default imports and aliases that almost every class needs.
header = """using System;
using Godot;
using Dictionary = Godot.Collections.Dictionary;
using Array = Godot.Collections.Array;
""";

export_replacements = {
	"export_range":"Export(PropertyHint.Range,",
	"export_exp_easing ": "Export(PropertyHint.ExpEasing)",
	"export_color_no_alpha":"Export(PropertyHint.ColorNoAlpha)",
	"export_flags":"Export(PropertyHint.Flags,",
	"export_enum":"Export(PropertyHint.Enum,",
	# TODO: fill more if needed /possible
}

variable_replacements = {
	"PI":"Mathf.Pi",
	"TAU":"Mathf.Tau",
	"INF":"Mathf.Inf",
	"NAN":"Mathf.NaN",
	"self":"this",
	"TYPE_ARRAY":"typeof(Array)",
	"TYPE_BOOL":"typeof(bool)",
	"TYPE_COLOR":"typeof(Color)",
	"TYPE_DICTIONARY":"typeof(Dictionary)",
	"TYPE_INT":"typeof(int)",
	"TYPE_NIL":"null",
	"TYPE_OBJECT":"typeof(Godot.Object)",
	"TYPE_REAL":"typeof(double)",
	"TYPE_RECT2":"typeof(Rect2)",
	"TYPE_RID":"typeof(RID)",
	"TYPE_STRING":"typeof(string)",
	"TYPE_VECTOR2":"typeof(Vector2)",
}

functions_override = [
	"_ready",
	"_process",
	"_physics_process"
]

function_replacements = {
	"Color8":"Color.Color8",
	"type_exists":"GD.TypeExists",
	"var2str":"GD.Var2Str",
	"str2var":"GD.Str2Var",
	"str":"GD.Str",
	"range":"GD.Range",
	"rand_seed":"GD.RandSeed",
	"rand_range":"GD.RandRange",
	"randomize":"GD.Randomize",
	"randi":"GD.Randi",
	"randf":"GD.Randf",
	"seed":"GD.Seed",
	"var2bytes":"GD.Var2Bytes",
	"bytes2var":"GD.Bytes2Var",
	"print":"GD.Print",
	"print_stack":"GD.PrintStack",
	"prints":"GD.PrintS",
	"printraw":"GD.PrintRaw",
	"printerr":"GD.PrintErr",
	"push_error":"GD.PushError",
	"push_warning":"GD.PushWarning",
	"load":"GD.Load",
	"preload":"/* preload has no equivalent, add a 'ResourcePreloader' Node in your scene */",
	"linear2db":"GD.Linear2Db",
	"db2linear":"GD.Db2Linear",
	"hash":"GD.Hash",
	"instance_from_id":"GD.InstanceFromId",
	"funcref":"GD.FuncRef",
	"dectime":"GD.DecTime",
	"convert":"GD.Convert",
	"assert":"System.Diagnostics.Debug.Assert",
	"max":"Mathf.Max",
	"min":"Mathf.Min",
	"abs":"Mathf.Abs",
	"acos":"Mathf.Acos",
	"asin":"Mathf.Asin",
	"atan":"Mathf.Atan",
	"atan2":"Mathf.Atan2",
	"cartesian2polar":"Mathf.Cartesian2Polar",
	"ceil":"Mathf.Ceil",
	"char":"Char.ConvertFromUtf32",
	"clamp":"Mathf.Clamp",
	"cos":"Mathf.Cos",
	"cosh":"Mathf.Cosh",
	"decimals":"Mathf.StepDecimals",
	"deg2rad":"Mathf.Deg2Rad",
	"ease":"Mathf.Ease",
	"exp":"Mathf.Exp",
	"floor":"Mathf.Floor",
	"fmod":"Mathf.PosMod",
	"fposmod":"Mathf.PosMod",
	"inverse_lerp":"Mathf.InverseLerp",
	"is_equal_approx":"Mathf.IsEqualApprox",
	"is_inf":"Mathf.IsInf",
	"is_nan":"Mathf.IsNaN",
	"is_zero_approx":"Mathf.IsZeroApprox",
	"lerp":"Mathf.Lerp",
	"lerp_angle":"Mathf.LerpAngle",
	"log":"Mathf.Log",
	"move_toward":"Mathf.MoveToward",
	"nearest_po2":"Mathf.NearestPo2",
	"ord":"Char.ConvertToUtf32",
	"parse_json":"Godot.JSON.Parse",
	"polar2cartesian":"Mathf.Polar2Cartesian",
	"posmod":"Mathf.PosMod",
	"pow":"Mathf.Pow",
	"preload":"GD.Load",
	"rad2deg":"Mathf.Rad2Deg",
	"range_lerp":"Mathf.Lerp",
	"round":"Mathf.Round",
	"seed":"GD.Seed",
	"sign":"Mathf.Sign",
	"sin":"Mathf.Sin",
	"sinh":"Mathf.Sinh",
	"smoothstep":"Mathf.Smoothstep",
	"sqrt":"Mathf.Sqrt",
	"step_decimals":"Mathf.StepDecimals",
	"stepify":"Mathf.Stepify",
	"tan":"Mathf.Tan",
	"tanh":"Mathf.Tanh",
	"to_json":"Godot.JSON.Print",
	"wrapf":"Mathf.Wrap",
	"wrapi":"Mathf.Wrap",
}