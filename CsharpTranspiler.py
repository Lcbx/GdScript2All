from io import StringIO as stringBuilder
import godot_types as ref


class CSharpTranspiler:
	
	def __init__(self):
		# scope level
		self.level = 0
		
		# allows to parse code and rearrange it
		self.layers = [stringBuilder()]
		
		# default imports
		self += ref.header
		
		# onready assignments that need to be moved to the ready function
		self.onready = []
		
		# unnamed enums don't exist in C#, so we use a counter to give them a name
		self.unnamed_enums = 0
	
	# += operator override to generate code
	def __iadd__(self, txt):
		# automatic indentation
		if '\n' in txt: txt = txt.replace('\n', '\n' + '\t' * self.level)
		self.write(txt)
		#print(">", txt.replace("\n", "<EOL>").replace('\t', '  '))
		return self
	
	def write(self, txt):
		self.layers[-1].write(txt)
	
	def get_result(self):
		#while len(self.layers) > 1: self += self.popLayer()
		#while self.level > 0: self.DownScope()
		return self.layers[0].getvalue()
	
	def UpScope(self):
		#print("UpScope")
		self += "\n{"
		self.level += 1
		#self += "\n"
	
	def DownScope(self):
		#print("DownScope")
		self.level -= 1
		self += "\n}"
	
	# layers : used for method definition
	# so we can parse return type then add code
	
	def addLayer(self):
		self.layers.append(stringBuilder())
		
	def popLayer(self):
		# add top scope txt to lower then remove top
		scope = self.layers[-1].getvalue()
		self.layers.pop()
		return scope
	
	
	def line_comment(self, content):
		self += f"//{content}"
	
	def multiline_comment(self, content):
		self += f"/*{content}*/"
	
	def end_statement(self):
		self += ';'
	
	def define_class(self, name, base_class, is_tool):
		if is_tool: self += '[Tool]\n'
		if base_class in ref.godot_types: base_class = f'Godot.{base_class}'
		self += f'public partial class {name} : {base_class}'
		self.UpScope()
		self += '\n'
	
	# NOTE: enums have similar syntax in gdscript, C# and cpp
	# lazily passing the enum definition as-is for now
	def enum(self, name, definition):
		# unnamed enums not supported in C#
		if not name:
			name  = f'Enum{self.unnamed_enums}'
			self.unnamed_enums += 1
		self += f'enum {name} {definition}'
	
	def annotation(self, name, params):
		# TODO: check replacements are exhaustive
		# https://docs.godotengine.org/en/stable/tutorials/scripting/gdscript/gdscript_exports.html
		# https://docs.godotengine.org/en/stable/tutorials/scripting/c_sharp/c_sharp_exports.html
		name = ref.export_replacements[name] if name in ref.export_replacements else toPascal(name) + (params and '(')
		self += f'[{name}"{params}")]' if params else f'[{name}]'
	
	
	def declare_property(self, type, name, constant, static):
		type = translate_type(type)
		const_decl = 'const ' if constant else 'static ' if static else ''
		exposed = 'protected' if name[0] == '_' else 'public'
		self += f'{exposed} {const_decl}{type} {name}'
	
	def declare_variable(self, type, name):
		self += f'var {name}'
	
	def assignment(self, exp):
		self += ' = '; get(exp)
	
	def subexpression(self, expression):
		self += '('; get(expression); self += ')'
	
	def create_array(self, values):
		self += 'new Array{'
		for value in values:
			get(value); self += ','
		self += '}'
		
	def create_dict(self, kv):
		self += 'new Dictionary{'
		for key, value in kv:
			self += '{'; get(key); self += ','; get(value); self+= '},'
		self += '}'
	
	def literal(self, value):
		# strings
		if isinstance(value, str):
			# add quotes / escape the quotes inside if necessary
			if '\n' in value: value = f'@"{value}"'
			else:
				value = value.replace('"', '\\"')
				value = f'"{value}"'
		
		# booleans
		elif isinstance(value, bool):
			self += str(value).lower(); return
		
		self += str(value)
	
	def constant(self, name):
		# Note: in c++ this would be ::<name>
		self += '.' + name
	
	def this(self):
		self += 'this.'
	
	def variable(self, name):
		name = 'this' if name == 'self' else name
		self += name
	
	def singleton(self, name):
		self += translate_type(name)
	
	def reference(self, name):
		self += '.' + name
	
	def call(self, name, params):
		self += name + '('
		for p in params[:-1]:
			get(p); self += ','
		if len(params)>0: get(params[-1])
		self += ')'
	
	def constructor(self, name, params):
		self += 'new '
		self.call(name, params)
	
	def subscription(self, key):
		self+= '['; get(key); self += ']'
		
	def operator(self, op):
		op = '&&' if op == 'and' \
			else '||' if op == 'or' \
			else '!' if op == 'not' \
			else op
		if op == '!': self += op
		else: self += f' {op} '
	
	def ternary(self, condition, valueIfTrue, valueIfFalse):
		self += '( '; get(condition); self += ' ? ';
		get(valueIfTrue); self += ' : '
		get(valueIfFalse); self += ' )'
	
	def define_method(self, name, params, params_init, return_type, static):
		
		# TODO: check if called _ready and at script level (self.level==1)
		# then add onready assignments first and clear onready array
		
		return_type = translate_type(return_type)
		
		blockText = self.popLayer()
		exposed = 'protected' if name[0] == '_' else 'public'
		static_str = 'static ' if static else ''
		self += f'{exposed} {static_str}{return_type} {name}('
		
		for i, (pName, pType) in enumerate(params.items()):
			if i != 0: self += ', '
			self += f'{translate_type(pType)} {pName}'
			if pName in params_init:
				self += ' = '; get(params_init[pName])
		
		self += ')'
		
		#self.UpScope()
		self.write(blockText)
	
	def returnStmt(self, return_exp):
		self += 'return '; get(return_exp)
	
	def end_script(self):
		# TODO: add ready function if missing and there are onready assignements in onready array
		# TODO: in cpp, add member and method bindings
		
		# end script-level class
		self.DownScope()

## Utils

def toPascal(text):
	text0is_ = text[0] == '_'
	if text0is_: text[0] = '*' # trick to preserve first underscore
	val = text.replace("_", " ").title().replace(" ", "")
	if text0is_: val[0] = '_'
	return val

def translate_type(type):
	if type == None: return 'void'
	if type in ['Array', 'Dictionary']: return type
	if type in ref.godot_types: return f'Godot.{type}'
	if type.endswith('[]'): return f'Array<{type[:-2]}>'
	if type == 'float': return 'double' # C# uses doubles
	return type

# trick for generator values
get = next

# TODO: support special literals like:
# * floating exponents : 58e-10
# * base16 int : 0x8E
# * bineary int : 0b1010
# * raw strings r"hello"
# * string names &"name"
# * nodepath : ^"parent/child"

# TODO: support match statment
# TODO: support break statment
# TODO: support continue statment
# TODO : await => await ToSignal(....)"
# TODO: support self => this more
# TODO: support adding user-defined classes to ref.godot_type
# TODO: support 'as' keyword
# TODO : Rename {Builtin_Class}.aa_bb_cc to AaBbCc (Eg Engine.is_editor_hint)
# TODO : unnamed enums



"""

match_irrelevant = "((^\s*\n)|(\/\/.*\n))" # Irrelevant c#

any_char = "[\w\W]"
t0 = fr"(?<!\n)^" # start of input ( Should be \A if that token exists )
eof = fr"(?!\n)$" # end of input \z
separator = fr"([{{}}\[\]\s,:;=()])"
clean_separator = fr"([{{\[\n,:;=(])" # No value to the left
comment_or_empty = "((^\s*\n)|(^\s*\/\/.*\n))"
rpc = fr"(remote|master|puppet|remotesync|mastersync|puppetsync)";
access_modifiers = fr"(public|private|protected)"

func_prefix = fr"({rpc}|{access_modifiers}|virtual|override|static|async|const|readonly)" # Most of these are c#
reserved_keywords = fr"(public|static|var|const|foreach|for|while|if|else|switch|case|return|using|new)"
valid_name = fr"([_a-zA-Z]+[_\-a-zA-Z0-9]*(?<!{reserved_keywords}))" 
match_curlies = fr"(?<curlies>{{((?>[^{{}}]+)|(?&curlies))*}})" # Named group recursion on curled braces
match_braces = fr"(?<braces>\(((?>[^()]+)|(?&braces))*\))"
match_brackets = fr"(?<brackets>\[((?>[^\[\]]+)|(?&brackets))*\])"
builtin_constructors = fr"(String|Vector2|Rect2|Vector3|Color|Transform2D|Plane|Quat|AABB|Basis|Transform|NodePath|RID|Object|Array|Dictionary)"# gd builtins types. Ignore types that don't have matching constructor in c#, like float
builtin_type = fr"(bool|uint|int|float|double|string|object|sbyte|byte|long|ulong|short|ushort|decimal|char|DateTime)" # C# builtins
valid_bool = fr"(true|false|True|False)"
valid_int = fr"(-?[0-9]+)"
valid_string = fr"(\".*?(?<!\\)\")"
valid_string_term = fr"((?<!(#|//).*|\\)(\".*?(?<!\\)\"|\'.*?(?<!\\)\'))"
valid_gd_only_string_term = fr"((?<!(#|//).*|\\)('([^']|\\')*?'(?<!\\')))"
valid_float = fr"(-?([0-9]*\.[0-9]+|[0-9]+\.[0-9]*)f?)"
valid_array = fr"({match_brackets})" # GD Definition
valid_dictionary = fr"{match_curlies}" # GD Definition
valid_value = fr"({valid_bool}|{valid_string}|{valid_float}|{valid_int}|{valid_array}|{valid_dictionary})"
valid_value_c = fr"({valid_bool}|{valid_string}|{valid_float}|{valid_int})"
full_name = fr"({valid_name}((\.{valid_name})*))" # Full name, including all dot access_modifiers
op = fr"([\/%+\-*><]|\|\||&&|>=|<=|==|!=|\||&|\sin\s|\sas\s|\sis\s|\sand\s|\sor\s)" # Basic (binary) operators
op_l = fr"(new\s|!|not\s)" # Right binding operators
op_r = fr"((?<!\n\s*)({match_brackets}|{match_braces}|(?<=new[\t ]+{full_name}[\t ]*{match_braces}\s*){match_curlies}))" # Left binding operators. GD doesn't allow newline, cs does, for simplicity we won't allow them
#fcall = fr"(?<!public .*)({valid_name}\s*{match_braces}\s*{match_curlies}*)" # Deprecated, function call is now an op_r
aterm = fr"({valid_value}|{valid_name})" # Atomic Terms without access_modifiers (.)
aterm_c = fr"({valid_value_c}|{valid_name})" # Atomic Terms without access_modifiers (.)
sterm = fr"(?<sterm>({aterm})(\.{valid_name})*)" # Simple Terms without operators other than dot accessor
sterm_c = fr"(?<sterm>({aterm_c})(\.{valid_name})*)" # Simple Terms without operators other than dot accessor
#cterm = fr"{aterm}({op_r}(\.{full_name}){0,1})*"
cterm = fr"(?<cterm>({aterm}|\((?&cterm)\))(\s*?{op_r}|\.{valid_name})*)" # Closed Terms without operators other than access_modifiers of any kind
cterm_c = fr"(?<cterm>({aterm_c}|\((?&cterm)\))(\s*?{op_r}|\.{valid_name})*)" # Closed Terms without operators other than access_modifiers of any kind
valid_term_single = fr"({op_l}\s*)*{sterm}(\s*{op_r})*";
valid_term_single_c = fr"({op_l}\s*)*{sterm_c}(\s*{op_r})*";
valid_term_braced = fr"({op_l}\s*)*{match_braces}(\s*{op_r})*";
valid_term_combination = fr"(?<vtc>\((?&vtc)\)|{valid_term_single}|({valid_term_single}|{valid_term_braced})([\t ]*{op}[\t ]*({valid_term_single}|{valid_term_braced})|\.{valid_term_single})+)"
valid_term_combination_c = fr"(?<vtc>\((?&vtc)\)|{valid_term_single_c}|({valid_term_single_c}|{valid_term_braced})([\t ]*{op}[\t ]*({valid_term_single_c}|{valid_term_braced})|\.{valid_term_single})+)"
valid_term = valid_term_combination#fr"(?<termo>(?!\s)(({op_l})*\s*?({cterm}|\(\s*(?&termo)\s*?\))\s*?((\s*{op}\s*|\.)(?&termo))*))";
valid_term_c = valid_term_combination_c#fr"(?<termo>(?!\s)(({op_l})*\s*?({cterm_c}|\(\s*(?&termo)\s*?\))\s*?((\s*{op}\s*|\.)(?&termo))*))";
assignable = fr"({valid_name}(\.{valid_name}|{match_braces}|{match_brackets})*(?<!{match_braces}))" # Something that can be assigned to.
# valid_term = fr"(?!\s)(?<termo>({op_l})*\s*?({cterm}|\(\s*(?&termo)\s*?\))\s*?(\s*{op}\s*(?&termo))*)(?={separator})";
match_comments_old = fr"([ \t]*#.*$)"
match_comments_new = fr"([ \t]*\/\/.*$)"
match_eol = fr"(?<eol>({match_comments_old}|{match_comments_new}|[\t ])*?$)" # Remaining bits of the line, such as tabs, spaces, comments etc.
getter_setter = fr"(?={{\s*(get|set)){match_curlies}" # C# getter/setter block. Only valid within match_field_declaration or similar.
field_prefix = fr"({access_modifiers}|onready|override|static|const|readonly|delegate)"

# FINAL lexical words (These provide fixed named output groups and therefore should not be used elsewhere)
match_field_declaration = fr"(?<=[;\n]|{t0}[ \t]*)(?P<Attributes>(\[.*\]\s*)*)(?P<Prefixes>({field_prefix}[ \t]+)*)(?P<Type>var|const|{full_name})[ \t]+(?P<Name>{valid_name})([\t ]*:[\t ]*(?P<Type>{full_name})?)?(?=\s*[\n;=]|{getter_setter})(?![ \t]*\()";
match_full_function_gd = fr"(?P<A>[\t ]*)({func_prefix}[\t ]+)*func[\t ]+(?P<Name>{valid_name})[\t ]*(?P<Params>{match_braces})([\t ]*->[\t ]*(?P<R_Type>.*))*[ \t]*:(?P<Comments>.*)\n(?P<Content>((\1[\t ]+.*(\n|{eof}))|{comment_or_empty})*)"
match_full_function_cs = fr"(?P<A>[\t ]*)({func_prefix}[\t ]+)*(?P<R_Type>{full_name})[\t ]+(?P<Name>{valid_name})[\t ]*(?P<Params>{match_braces})[\t ]*(?P<Comments>.*)\s*(?P<Content>{match_curlies})"
match_type_hinting = fr"(?<!\/\/.*)(?<={valid_name}[\t ]*\( *.*)(?P<Name>{valid_name})[\t ]*:[\t ]*(?P<Type>{valid_name})"
match_function_arguments = fr"(?<=^\s*({func_prefix}[\t ]+)*{access_modifiers}+[\t ]+({valid_name}[\t ]+)?{valid_name}[\t ]*){match_braces}"
match_function_header = fr"(?<=^\s*)(?P<AccessModifiers>({func_prefix}[\t ]+)*{access_modifiers}+)[\t ]+((?P<Type>{valid_name})[\t ]+)?(?P<Name>{valid_name})[\t ]*(?P<Args>{match_braces})"
match_gd_node_path = fr"(\$(?P<Path>{valid_name}(\/{valid_name})*))"
match_class_cs = fr"class";


# Run code and return output
def run(code,variables = {}):
	results = variables
	exec(regex.sub(fr"([\t ]*)return ({valid_name}|{valid_value})",fr"\1__result = \2\n\1return \2",code,0,flags),globals(),results)
	return results["__result"];

def to_pascal(text):
	return (text[0].upper() + text[1:]) if len(text) > 0 else text;

def to_camel(text):
	return (text[0].lower() + text[1:]) if len(text) > 0 else text;

def snake_to_camel(text):
	components = text.split('_')
	return components[0] + ''.join(x.title() for x in components[1:])

def const_to_pascal(text):
	return (text[0].upper() + text[1:].lower()) if len(text) > 0 else text;

# Change function name to c# style
def rename_function(text):
	return text;

# Change field name to c# style
def rename_field(text):
	return text;

# Change local variable name to c# style
def rename_local_var(text):
	return text;

variable_replacements = [ # Anything that uses case conversions happens in the actual replacements array
	["PI","Mathf.Pi"],
	["TAU","Mathf.Tau"],
	["INF","Mathf.Inf"],
	["NAN","Mathf.NaN"],
	["self","this"],
	["TYPE_ARRAY","typeof(Array)"],
	["TYPE_BOOL","typeof(bool)"],
	["TYPE_COLOR","typeof(Color)"],
	["TYPE_DICTIONARY","typeof(Dictionary)"],
	["TYPE_INT","typeof(int)"],
	["TYPE_NIL","null"],
	["TYPE_OBJECT","typeof(Godot.Object)"],
	["TYPE_REAL","typeof(float)"], # TODO : Is this float or double?
	["TYPE_RECT2","typeof(Rect2)"],
	["TYPE_RID","typeof(RID)"],
	["TYPE_STRING","typeof(string)"],
	["TYPE_VECTOR2","typeof(Vector2)"],
]



def rename_builtin_vars(text):
	for pair in variable_replacements:
		pair[0] = fr"(?<={separator})(?<![.])" + pair[0] + fr"(?={separator})(?!\()";
		text = regex.sub(pair[0], pair[1], text,0,flags)
	return text


#  def match_inverse(pattern): # May not be so simple
#  	return fr"(?<={t0}|{pattern})([\s\S]*?)(?<=(?)\1)(?={pattern}|{eof})";

# Define the replacements. 
# This can either be an array with 2 values, the first of which will match the target text locations, and the second of which will define how the matched text will be transformed/replaced.
# Alternatively, it can be an object which matches a part of the string and passes it to children, who will then replace only the matched text.
# Furthermore this allows for arbitrary functions to modify the matched text.

replacements = [

	# DOCUMENTATION / EXAMPLE of new system :

	# {
	#	"repeat":False, # If False, only run this replacement once. Otherwise repeat until no more changes occur. Default True
	#	"inverted":True, # If true, match all parts of the text that do NOT match "match". Essentially split the text by "match" and continue with the split parts individually.
	# 	"match":fr"return", # Match text to this. Pass result to children and/or replacement regex if it exists
	#	"match_group":"Name", # Limit the selection to only 1 group from match. This way big statements can be reused (slower, but more compact and readable)
	# 	"children":[
	# 		{
	# 			"replacement":[fr"r",fr"bed"]
	# 		}
	# 	], # Children get matched contents of parent. If multiple children, subsequent children receive the modified versions (these may not necessarily still match the original pattern)
	#      # Children can also be a dictionary, in which case each key is equivalent to match_group. For technical reasons none of the groups can overlap though.
	# 	"replacement":[fr"(.*)",r"\1"], # Match result strings of match (or input text if match is undefined) after the children are done with it and do regex replace
	# 	"replacement_f": lambda v: run("__result = v",{"v":v}) # Excecuted after everything else is done. Used by any rules that cannot be put into simple regex
	# },

{
	"repeat":False,
	"match": fr"[\w\W]*",
	"children":
	[
		# Add an empty line at the end of the document so the {} formatting turns out prettier if there is no empty line there already
		{
			"repeat":False,
			"replacement":[fr"{eof}","\n"],
		},
		# Replace spaces at beginning of line with tabs where applicable (Required for offset/scope matching)
		[fr"(?<=^\t*)" + fr" "*strip_tabs,fr"\t"],
		# Clean up directives that are manually applied after regex replacements
		[fr"^\s*@?tool\s*$"," "], 
		[fr"^\s*extends\s*.*\s*$"," "],
		[fr"^\s*class_name\s*.*\s*$"," "], # Class Name is ignored entirely. C# Classes must be named like the file they are in.
		[fr"\$\s*(?P<A>{valid_string_term})",fr"GetNode(\g<A>)"],
		# Builtin constructors, like "Vector2()" => "new Vector2()"
		[fr"(?<={separator})(?<!new\s+)(?P<A>\s*)(?P<B>{builtin_constructors})\s*\(",fr"\g<A>new \g<B>("],
		# Turn lowest level unprocessed dictionaries. KV pairs are still of form K:V though
		[fr"(?<!(new Dictionary\(\)|new Array\(\)))(?<=([:,={{[(]|return\s+))(?P<W>{match_eol}*\s*)(?P<C>{match_curlies})",r"\g<W>new Dictionary()\g<C>"], 
		# Same for array
		[fr"(?<!(new Dictionary\(\)|new Array\(\)))(?<=([:,={{[(]|return\s+))(?P<W>{match_eol}*\s*)(\[(?P<C>([^\[]|(?R))*?)\])",r"\g<W>new Array(){\g<C>}"],
		# Chars don't exist in gdscript, so let's assume all of those '-strings are normal "-strings.
		# {
		# 	"repeat":False,
		# 	"match":fr"{valid_string_term}",
		# 	"replacement":[fr"(?<=^@?)'(.*)'$",fr'"\1"']# Single quote to double quote since in c# single quotes denote chars
		# },
		# Turn single quote strings into double quote ones. Format the string's content to match.
		{
			"repeat":False,
			"match":fr"{valid_gd_only_string_term}", # Single quotes only
			"children":[
				{
					"match":fr"(?<=^(\"|'))[\s\S]*(?=(\"|')$)", # Match string content only
					"replacement":[fr"(?<!\\)\"",fr"\""], # Escape double quotes since new string will now be escaped via double quotes
					
				}
			],
			"replacement":[fr"(?<=^@?)'([\w\W]*)'$",fr'"\1"'], # Single quote to double quote since in c# single quotes denote chars
			#"replacement_f":lambda f : print(f) or f
			
		},
		# Anything not in a string
		{ 
			"inverted":True,
			"match":fr"{valid_string_term}",
			"children":
			[
				{ # Anything not in a comment
					"inverted":True,
					"match":fr"(?<=(#|\/\/).*).*$", 
					"children":[
						{
							"replacement":[fr"#",fr"//"]# Single line comments from # to //
						},
						{
							"replacement":[match_gd_node_path,fr'GetNode("\g<Path>")'],
							#"replacement_f":lambda a,b:print(a) or a
						}

					]
				}
			]
			
		},
		# Variant is System.Object in C#
		[fr"(?<={separator})Variant(?={separator})",fr"System.Object"],
		# For loops
		[fr"(?<=\n)([\t ]*)for[\t ]+(.*)(->(.*))*:(.*)\n(((\1[\t ]+.*\n)|{comment_or_empty})*)",r"\1foreach(var \2)\5\n\1{\n\6\1}\n"], 
		# While loops
		[fr"(?<=\n)([\t ]*)while[\t ]+(?P<Condition>.*):(?P<B>(.*)\n)(?P<Content>((\1[\t ]+.*(\n|{eof}))|{comment_or_empty})*)",r"\1while(\g<Condition>)\g<B>\1{\n\g<Content>\1}\n"], 
		
		
		# "a:B" to "B a" ; Both in function calls and definitions as well as field declarations etc
		[match_type_hinting,r"\g<Type> \g<Name>"], 

		## Functions

		# Match Function Defintions
		{ 
			"repeat":False,
			"match":match_full_function_gd,
			"children":[
				{
					"repeat":False,
					# replace function declarations, if possible use return type, otherwise leave blank
					"replacement":[match_full_function_gd,r"\1public \g<R_Type> \g<Name>\g<Params>\n\1{\1  \g<Comments>\n\g<Content>\1}\n\n"],
					#"replacement_f":lambda v: print("\n-------\n"+v) or v
				},
				{
					"repeat":False,
					"match":match_function_arguments,
					"children":[
						{# autocomplete function arguments via default values (bool). First limit selection to function signature, then run replacement over that section only.
							"replacement":[fr"(?<=[,(]\s*?)(?P<A>{valid_name}\s*=\s*{valid_bool})",fr"bool \g<A>"]
						},
						{# autocomplete function arguments via default values (int)
							"replacement":[fr"(?<=[,(]\s*?)(?P<A>{valid_name}\s*=\s*{valid_int})",fr"int \g<A>"]
						},
						{# autocomplete function arguments via default values (string)
							"replacement":[fr"(?<=[,(]\s*?)(?P<A>{valid_name}\s*=\s*{valid_string})",fr"string \g<A>"]
						},
						{# autocomplete function arguments via default values (float)
							"replacement":[fr"(?<=[,(]\s*?)(?P<A>{valid_name}\s*=\s*{valid_float})",fr"float \g<A>"]
						},
						{# autocomplete function arguments via default values (new T)
							"replacement":[fr"(?<=[,(]\s*?)(?P<A>{valid_name}\s*=\s*new\s+(?P<Name>{full_name}))",fr"\g<Name> \g<A>"]
						},
						{# autocomplete function arguments via default values (new T)
							"replacement":[fr"(?<=[,(]\s*?)(?P<A>{valid_name}\s*=\s*new\s+(?P<Name>{full_name}))",fr"\g<Name> \g<A>"]
						},
						{# autocomplete function arguments without any implicit or explicit type hinting. Use __TYPE to denote user input being required.
							"replacement":[fr"(?<=[,(]\s*?)(?P<A>{valid_name}\s*)(?=\s*[=,)])",fr"__TYPE \g<A>"]
						}
					]
				},
				{
					"repeat":False,
					"match":fr"[\w\W]*{separator}await\s+", # Skip if the function doesnt contain the keyword yield, otherwise continue with its entirety
					"children":[
						{
							"replacement":[fr"(?<={access_modifiers}+)(?![ \t]+async)",fr" async"], # Add async to function signature, right after "public"
							#"replacement_f":lambda v: print("A",v) or v
						}
					],
					
				},
				{ # Set return type to void if no return __TYPE; exists
					"repeat":False,
					"match":fr"{t0}(?![\w\W]*(?<!\/\/[^\n]*)return[ \t]+{valid_term}[\w\W]*)[\w\W]*", # Skip if the function contains a valued return, else continue in full
					"children":[
						{
							"replacement":[fr"(?<=(^|\s)({func_prefix})+)[\t ]*(?=[\t ]*{valid_name}[ \t]*\()",fr" void "],
						}
					],
					
				},
				{ # Method doesnt have a valid return type
					"repeat":False,
					"replacement":[fr"(?<=(^|\s)({func_prefix})+)[\t ]*(?=[\t ]*{valid_name}[ \t]*\()",fr" __TYPE "],
					#"replacement_f":lambda v: v
				}
			],
		},

		# .functionCall() => base.functionCall()
		[fr"(?<={clean_separator}\s*)(?=\.{valid_name}[\t ]*\()",fr"base"],
		{ # Any class field (~variable declaration outside of function bodies) 
			"inverted":True,
			"match":match_full_function_cs,
			"children":[
				[fr"(?<=[\n;][\t ]*)var(?=[\t ]+{valid_name}[\t ]*(=|\n|;))",fr"__TYPE"], # must have a well defined type. Replace var with __TYPE to notify user this needs to be defined manually.
				[fr"(?<=[\n;][\t ]*)(?!.*{access_modifiers})(?=({field_prefix}[\t ]*)*{full_name}[\t ]+[a-zA-Z]{valid_name}?[\t ]*(=|\n|;|setget))","public "],
				[fr"(?<=[\n;][\t ]*)(?!.*{access_modifiers})(?=({field_prefix}[\t ]*)*{full_name}[\t ]+{valid_name}[\t ]*(=|\n|;|setget))","private "], # Private if it starts with _ or other weird character

			],
			#"replacement_f":lambda v: print("----- FUNC -----\n",v) or v
		},

		## If/Else
		
		# replace if/elif blocks 
		[fr"^(?P<A>[ \t]*)(?P<B>if|elif)(?=[\t \(])[\t ]*(?P<C>{valid_term}{{1,1}})[ \t]*:(?P<Comment>{match_eol})(?P<E>\n({comment_or_empty}*(\1[\t ]+.*(\n|{eof}))*)*)",r"\g<A>\g<B>(\g<C>)\g<Comment>\n\g<A>{\g<E>\g<A>}\n"], 
		# single line if/else : * (This must not capture subsequent indendented lines)
		[fr"^(?P<A>[ \t]*)(?P<B>if|elif)(?=[\t \(])[\t ]*(?P<C>{valid_term}{{1,1}})[ \t]*:(?P<D>[^\n]*?)(?P<Comment>{match_eol})",r"\g<A>\g<B>(\g<C>)\g<Comment>\n\g<A>\t\g<D>"], 
		# elif
		[fr"(?<={separator})elif(?={separator})","else if"],
		# replace else
		[fr"^(?P<A>[ \t]*)(?P<B>else)[\t ]*:(?P<D>[^\n]*)\n(?P<E>((\1[\t ]+.*(\n|{eof})|{comment_or_empty})*))",r"\g<A>\g<B>\g<D>\n\g<A>{\n\g<E>\g<A>}\n"],
		# inline if else
		[fr"((?=[^\n]*[\t ]+if[ \t]+[^\n]+[ \t]+else[ \t]+[^\n]+)(?P<A>{valid_term})[ \t]+if[ \t]+(?P<B>{valid_term})[ \t]+else[ \t]+(?P<C>{valid_term}))",fr"\g<B> ? \g<A> : \g<C>"],

		## Variable Declarations

		# Remove trailing colon if it didnt have an explicit type
		[fr"(?<=(\s|^)var\s+{valid_name}\s*):(?=\s*(=))",fr" "], 
		# Variable definitions, if they have a valid type
		[fr"var[\t ]+(?P<Name>{valid_name})[\t ]*:[\t ]*(?P<Type>{valid_name})",r"\g<Type> \g<Name>"], 
		# Signals
		[fr"(?<={separator})signal(?P<R>\s+{valid_name}\s*{match_braces})[\t ]*\;*(?={match_eol})",fr"[Signal] delegate void\g<R>;"],
		# Unidentifiable variables const var
		[fr"(?<={separator}const\s+)(?={valid_name}\s*:?\s*(=|setget))",r"var "], 
		# Auto identify variables from export hints
		[fr"(?<={separator})@?export\s*\(\s*(?P<T>{valid_term})\s*(,\s*(?P<A>.*?)?)\s*\)\s*(?P<B>(const\s+)?)(var|const|{full_name})(?=\s+{valid_name}\s*(=|setget|;))",fr"[Export(\g<A>)] \g<B> \g<T>"], # Has parameters => Can derive type
		[fr"(?<={separator})@?export\s*\(\s*(?P<T>{valid_term})\s*\)\s*(?P<B>(const\s+)?)(var|const|{full_name})(?=\s+{valid_name}\s*(=|setget|;))",fr"[Export] \g<B> \g<T>"], # Has parameters => Can derive type
		[fr"(?<={separator})@?export\s*(?P<B>(const\s+)?)(?=(var|const|{full_name})\s+{valid_name}\s*(=|setget|;))",fr"[Export] \g<B>"], # No parameters
		# Auto identify bools. TODO : Also accept simple static terms such as 5*5, !true, "a" in ["a","b","c"]
		[fr"(?<={separator})var(?=\s+{valid_name}\s*:?\s*=\s*{valid_bool}(.*))",r"bool"],
		# Auto identify float
		[fr"(?<={separator})var(?P<A>\s+{valid_name}\s*:?\s*=\s*{valid_float})",r"float\g<A>f"],  
		# Auto identify integers. 
		[fr"(?<={separator})var(?=\s+{valid_name}\s*:?\s*=\s*{valid_int}(.*))",r"int"], 
		# Auto identify string
		[fr"(?<={separator})var(?=\s+{valid_name}\s*:?\s*=\s*{valid_string}(.*))",r"string"], 
		# Auto identify Object
		[fr"(?<=\s|^)var\s+(?P<A>{valid_name})(?=\s*:?\s*=\s*new\s+(?P<B>{full_name})(.*))",fr"\g<B> \g<A>"], 
		# const => static readonly unless value is struct
		[fr"const[\t ]+(?!{builtin_type}[\t ])(?={valid_name}[\t ]+{valid_name}[\t ]+(=|setget))",fr"static readonly "],
		# setget
		[fr"(?<=\s)setget[ \t]+(?P<S>{valid_name})((,)[ \t]*(?P<G>{valid_name}))",r"{get{return \g<G>();} set{\g<S>(value);}}"],
		[fr"(?<=\s)setget[ \t]+(?P<S>{valid_name})",r"{set{\g<S>(value);}}"], 
		[fr"(?<=\s)setget[ \t]+((,)[ \t]*(?P<G>{valid_name}))",r"{get{return \g<G>();}}"],

		## Operators

		# not => !
		[fr"(?<={separator})not(?=[\s(])\s*","!"], 
		# Direct casts
		[fr"(?<={separator})(\s*){builtin_type}\s*\(",fr"\2(\3)("], 
		# typeof(v) => v.GetType()
		[fr"(?<={separator}\s*)typeof\s*{match_braces}",r"\2.GetType()"], 
		# TODO : Don't affect strings and comments
		[r"(?<=\s)and(?=\s)","&&"], 
		[r"(?<=\s)or(?=\s)","||"],
		# [fr"{cterm}\s+in\s+{cterm}",fr""] # Ignore "in" operator for now due to complicated operator binding situation.
		# Turn all remaining A : B into automatic array pairs {A,B} , presumably part of dictionary initiation.
		[fr"(?<! \/\/.*)(\"(([^\"]|\\\")*?)((?<!\\)\"))(\s*)(:)(((?<curlies>{{((?>[^{{}}]+)|(?&curlies))*}})|([^{{]))*?)(?=}}|,)",r"{\1,\7}"],


		## SWITCH/CASE

		# Multistep. Match iteratively on previous match only. Last match is used with replacement regex. Then all pieces are merged back together again. This is me surrendering to the almighty switch/case pattern, which I just can't manage to squeeze into a single regex replacement line. I know possessive quantifiers should be able to help here, but the effort is just not worth it since I don't have a testing tool that supports those
		[[fr"^([ \t]*)match[ \t]+(.*)[ \t]*:.*\n({comment_or_empty}|\1[ \t]+.*\n)*",fr"^([ \t]*)(?!case)(({valid_term}(\s*,\s*{valid_term})*)[ \t]*:(.*)\n({comment_or_empty}|\1[ \t]+.*\n)*)"],fr"\1case \2\1\tbreak;\n"], 
		# Continue switch case : turn match to switch and surround with curlies.
		[fr"^(?P<A>[ \t]*)match(?P<B>[ \t]+{valid_term}[ \t]*):(?P<C>[ \t]*(\/\/.*)*\n)(?P<D>({comment_or_empty}|\1[ \t]+.*\n)*)",fr"\g<A>switch(\g<B>)\g<C>\g<A>{{\n\g<D>\g<A>}}\n"],
		# C# Doesn't support multiple cases in one line, so split them
		[fr"^(?P<A>\s+)case\s+(?P<B>{valid_term})\s*,\s*(?P<C>({valid_term},)*{valid_term})\s*:",fr"\g<A>case \g<B>:\n\g<A>case \g<C>:"], 

		## SEMICOLONS

		# semicolon at end of standalone terms (such as function calls) (but never after values like new T() or {valid_value})
		[fr"(?<![,]\s*)(?<=^[ \t]*)(?!{reserved_keywords}\s*\(*)(?P<Content>{valid_term_c}[ \t]*)(?P<Comment>{match_eol})(?!\s*[{{[(])",fr"\g<Content>;\g<Comment>"], 
		#[fr"(?<![,]\s*)(?<=^[ \t]*)(?!{reserved_keywords}\s*\(*)(?P<Content>{valid_term_c}[ \t]*)(?P<Comment>{match_eol})(?!\s*[{{[(])",fr"\g<Content>;\g<Comment>"], 
		# semicolon after var X\n
		[fr"(?<=var[\t ]+{valid_name})(?=[ \t]*\n)",fr";"],
		[fr"(?<={access_modifiers}[\t ]+{full_name}[\t ]+{valid_name})(?=[ \t]*\n)",fr";"],
		# semicolon at end of assignments TODO : Super expensive
		[fr"((?<=^[ \t]*|((var|const|public|private|static|async|delegate|{match_brackets})[ \t])*)({valid_name}[\t ]+)?{assignable}[\t ]*[\+\-]?=[\t ]*{valid_term_c}[ \t]*)(?P<E>{match_eol})(?!\s*[{{(,])",fr"\1;\g<E>"],
		# return statements TODO : May be surrounded by braces or curlies, which will not count as ^ or $ 
		[fr"^(?P<A>[ \t]*return([\t ]*{valid_term_c})?)(?P<B>{match_eol})",fr"\g<A>;\g<B>"], 

		## Cleanup

		
		# Strip "pass", which is replaced already by (maybe empty) curlies.
		[fr"^[\t ]*pass[\t ]*;*[\t ]*\n",""], 
		
		# Replace constants (multiple different names that follow clear patterns)
		{
			"match":fr"(?<={separator})PROPERTY_USAGE_([A-Z]*_?)*", # PROPERTY_USAGE_*
			"children":[
				{
					"match":fr"(?<=PROPERTY_USAGE_).*", # First turn to PascalCase
					"replacement_f":lambda t,m: regex.subf(fr"[A-Z]+",lambda s: const_to_pascal(s.group(0)),t,0,flags),
				},
				{ # Then strip spaces
					"replacement":["_",""],
				}
			],
			"replacement":[
				fr"PROPERTYUSAGE(?P<Name>.*)",
				fr"Godot.PropertyUsageFlags.\g<Name>"
			]
		},

		# { # Turn multiline strings into string additions
		# 	"repeat":False,
		# 	"match":fr"(?<!(#|//).*)(\"([^\"]|\\\")*?(?<!\\)\")", # In C# common strings can't be multiline. But the previous regex can produce them. In that case, we match all  strings, including these "bad" strings here
		# 	"children":[
		# 		{
		# 			"repeat":False,
		# 			"replacement":[fr"\n",r'\\n"+\n"'],# Split on linebreak
		# 		}
		# 	],
		# 	#"replacement_f": lambda v: print(v) or v
			
		# },
		{
			"replacement": [fr"({full_name}).new\(\)",fr"new \1()"] # Should match valid_term instead of full_name, but that wouldn't take op precedence into account, so use full_name for the time being until a weak valid term alternative is defined ( TODO )
		},
		{ # Rename all function calls and definitions
			"requirement":lambda : rename_functions != 0,
			"repeat":False,
			"match":fr"(?<={separator}|[.]){valid_name}(?=[\t ]*[(])",
			"children":[
				{
					"repeat":False,
					"inverted":True,
					"match":fr"_",# Split on underscore
					"replacement_f":lambda t,m : to_pascal(t)
				},
				{
					"repeat":False,
					"replacement":[fr"(?<!^_*)_",fr""]
				}
			]
		},
		{
			"replacement_f":lambda a,b : rename_builtin_vars(a),
		},
		{ # Rename all fields
			"repeat":False,
			"match":match_field_declaration,
			"children":{
				"Name":[
					{
						"requirement":lambda : rename_vars != 0,
						"repeat":False,
						"match":fr"(?!_).*",# ignore leading underscores
						"replacement_f": lambda t,m : snake_to_camel(t)
					}
				],
				"Prefixes":[
					{
						"repeat":False,
						"replacement":[fr"^(?![\s\S]*((\s|^){access_modifiers}(\s|$)))","public "], # If no public/private/protected
						#"replacement_f":lambda f,a : print("Pref " + f) or f
					}
				]
			},
			#"replacement_f":lambda t,m : print("Full" , t) or t,
		},
		{ # Rename all accessed properties and local variables
			"match":fr"(?<={separator}){valid_name}(?![\t ]*\()",
			"children":
			[
				{
					"requirement":lambda : rename_vars != 0,
					"repeat":False,
					"match":fr"(?!_).*",# ignore leading underscores
					"replacement_f": lambda t,m : snake_to_camel(t)
				}
			]
		}
	]
}
		
	

];


function_replacements = [
	["yield","await ToSignal"],
	["Color8","Color.Color8"],
	["type_exists","GD.TypeExists"],
	["var2str","GD.Var2Str"],
	["str2var","GD.Str2Var"],
	["str","GD.Str"],
	["range","GD.Range"],
	["rand_seed","GD.RandSeed"],
	["rand_range","GD.RandRange"],
	["randomize","GD.Randomize"],
	["randi","GD.Randi"],
	["randf","GD.Randf"],
	["seed","GD.Seed"],
	["var2bytes","GD.Var2Bytes"],
	["bytes2var","GD.Bytes2Var"],
	["print","GD.Print"],
	["print_stack","GD.PrintStack"],
	["prints","GD.PrintS"],
	["printraw","GD.PrintRaw"],
	["printerr","GD.PrintErr"],
	["push_error","GD.PushError"],
	["push_warning","GD.PushWarning"],
	["load","GD.Load"],
	["linear2db","GD.Linear2Db"],
	["db2linear","GD.Db2Linear"],
	["hash","GD.Hash"],
	["instance_from_id","GD.InstanceFromId"],
	["funcref","GD.FuncRef"],
	["dectime","GD.DecTime"],
	["convert","GD.Convert"],
	["assert","System.Diagnostics.Debug.Assert"],
	["max","Mathf.Max"],
	["min","Mathf.Min"],
	["abs","Mathf.Abs"],
	["acos","Mathf.Acos"],
	["asin","Mathf.Asin"],
	["atan","Mathf.Atan"],
	["atan2","Mathf.Atan2"],
	["cartesian2polar","Mathf.Cartesian2Polar"],
	["ceil","Mathf.Ceil"],
	["char","Char.ConvertFromUtf32"],
	["clamp","Mathf.Clamp"],
	["cos","Mathf.Cos"],
	["cosh","Mathf.Cosh"],
	["decimals","Mathf.StepDecimals"],
	["deg2rad","Mathf.Deg2Rad"],
	#["dict2inst","Mathf.Abs"],
	["ease","Mathf.Ease"],
	["exp","Mathf.Exp"],
	["floor","Mathf.Floor"],
	["fmod","Mathf.PosMod"],
	["fposmod","Mathf.PosMod"],
	#["get_stack","Mathf.Abs"],
	#["inst2dict","Mathf.Abs"],
	["inverse_lerp","Mathf.InverseLerp"],
	["is_equal_approx","Mathf.IsEqualApprox"],
	["is_inf","Mathf.IsInf"],
	#["is_instance_valid","Mathf.Abs"],
	["is_nan","Mathf.IsNaN"],
	["is_zero_approx","Mathf.IsZeroApprox"],
	#["len","Mathf.Abs"],
	["lerp","Mathf.Lerp"],
	["lerp_angle","Mathf.LerpAngle"],
	["log","Mathf.Log"],
	["move_toward","Mathf.MoveToward"],
	["nearest_po2","Mathf.NearestPo2"],
	["ord","Char.ConvertToUtf32"],
	["parse_json","Godot.JSON.Parse"],
	["polar2cartesian","Mathf.Polar2Cartesian"],
	["posmod","Mathf.PosMod"],
	["pow","Mathf.Pow"],
	["preload","GD.Load"],
	#["print_debug","Mathf.Abs"],
	["rad2deg","Mathf.Rad2Deg"],
	["range_lerp","Mathf.Lerp"],
	["round","Mathf.Round"],
	["seed","GD.Seed"],
	["sign","Mathf.Sign"],
	["sin","Mathf.Sin"],
	["sinh","Mathf.Sinh"],
	["smoothstep","Mathf.Smoothstep"],
	["sqrt","Mathf.Sqrt"],
	["step_decimals","Mathf.StepDecimals"],
	["stepify","Mathf.Stepify"],
	["tan","Mathf.Tan"],
	["tanh","Mathf.Tanh"],
	["to_json","Godot.JSON.Print"],
	#["validate_json","Mathf.Abs"],
	#["weakref","Mathf.Abs"],
	["wrapf","Mathf.Wrap"],
	["wrapi","Mathf.Wrap"],
	#["yield","Mathf.Abs"],
	["emit_signal","EmitSignal"],
	["connect","Connect"],
];



# Regex doesn't support recursion of groups that share a name with previously defined groups.
# The next 2 functions append a number to each group to make them unique to the compiler.
# (This should not affect the actual logic and can be safely ignored)
unique_number = 0
def make_group_unique(reg_data):
	global unique_number
	unique_number += 1

	precise_match = regex.match(fr"(\(\?\<([a-zA-Z]+)\>)(.*)\)",reg_data[0],flags);

	content = strip_duplicate_groups(precise_match[3])

	return (precise_match[1] + content + ')').replace(precise_match[2],precise_match[2]+str(unique_number))

# Recursion doesn't work with duplicate group names, so rename them if they don't already have a number suffix (suffix => presumed renamed)
def strip_duplicate_groups(reg):
	prev = reg
	result = regex.subf(fr"(?=\(\?\<([a-zA-Z])+\>)({match_braces})",make_group_unique,prev)
	return result


# Regex search flags. Multiline allows the use of ^ for the beginning of a line and $ for the end.
flags = regex.MULTILINE or regex.GLOBAL_FLAGS

# v:String text value
# obj
# m : regex.Match
def _object_replace_child_call(v: str, obj: object, m: regex.regex = None) -> str:

	

	if not 'children' in obj:
		obj['children'] = []

	if type(obj['children']) == list:
		for child in obj['children'] : 
			v = _try_replace(v,child); 
	else: # Dictionary
		#cache = {}
		if m == None:
			print("ERROR : Named Childgroups are only valid if parent is not inverted or otherwise transformed in a way that loses well defined groups.")
			for key,child in obj['children'].items() :
				v = _try_replace(v,child); 
		else:
			start = m.start(0)
			end = m.end(0)
			#print([method_name for method_name in dir(m) if callable(getattr(m, method_name))])
			cache = [] # Split the string into its groups and ungrouped segments individually so each replacement affects only its matched parts. Combine them later and don't worry about indices.
			cache_names = {} # name to cache index
			prev_i = 0
			for k in m.groupdict().keys():
				if k not in obj['children'].keys():
					continue
				#print('checking ', k, " ", m.start(k), m.end(k),v[m.start(k)-start:m.end(k)-start])
				cache.append(v[prev_i:m.start(k)-start]) # Potentially unnamed matched segment
				cache_names[k] = len(cache)
				cache.append(v[m.start(k)-start:m.end(k)-start]) # Named matched segment
				prev_i = m.end(k)-start
			cache.append(v[prev_i:len(v)]) # Potentially unnamed matched segment
			for key,child in obj['children'].items() :
				#
				#cache[key] = _try_replace(v[m.start(key):m.end(key)]
				#print(cache)
				#print("Repl ", key, " " ,cache, " vs ", cache_names[key])
				for c in child:
					#print("A")
					cache[cache_names[key]] = _try_replace(cache[cache_names[key]],c);
					#print("B")
				
			#print("from " , v)
			v = "".join(cache); # Recombine all grouped and ungrouped segments
			#print("to " , v)
	
	
	if 'replacement' in obj:
		v = _try_replace(v,obj['replacement'],obj.get('repeat',True));

	
	if 'replacement_f' in obj:
		v = obj['replacement_f'](v,m);



	return v

def object_replace(obj,text):

	if "requirement" in obj and not obj["requirement"]():
		return text # Requirement failed, don't do anything

	match = obj['match'] if 'match' in obj else False;
	
	if not match:
		match = r"^[\s\S]*$" # Match anything
	else:
		match = strip_duplicate_groups(match);
	
	inverted = obj['inverted'] if 'inverted' in obj else False
	
	matches = regex.finditer(match,text,flags)
	result = ""
	if inverted:
		prev_i = 0
		for m in matches:
			#print(m.captures())
			# print(text[prev_i:m.start()])
			# print(m.group(0))
			result += _object_replace_child_call(text[prev_i:m.start()],obj) + m.group(0)
			prev_i = m.end()


		result += _object_replace_child_call(text[prev_i:len(text)],obj)
	else:
		prev_i = 0
		match_group = 0
		if "match_group" in obj:
				match_group = obj["match_group"]
		#print(matches)
		for m in matches:
			result += text[prev_i:m.start(match_group)] + _object_replace_child_call(m.group(match_group),obj,m)

			prev_i = m.end(match_group)
		result += text[prev_i:len(text)]
		#print("D")
		#result = regex.subf(match,lambda v: _object_replace_child_call(v.group(0),obj,m),text,0,flags)


	text = result

	return text;

	



# Replace in multiple steps, by matching first
def array_replace(matches,replacement,text,depth=0):
	sub_segment = matches[depth];
	

	matches[depth] = strip_duplicate_groups(matches[depth])
	
	if len(matches)-1 == depth:
		loop_count = 0
		while True:
			loop_count+=1
			if loop_count > 100:
				print('Infinite loop detected')
				print(text)
				quit()
			prev_text = text
			text = regex.sub(matches[depth], replacement, text,0,flags)
			if text == prev_text: # Repeatedly apply same operation until no more changes occur.
				return text;
	else:
		result =  regex.subf(matches[depth],lambda v : array_replace(matches,replacement,v.group(0),depth+1) ,text,0,flags)
		return result;
	

def _try_replace(text,replacer,repeat = None):
	if repeat == None:
		repeat = not "repeat" in replacer or replacer["repeat"]


	orig_text = text;
	while True:
		prev_text = text
		if not isinstance(replacer, list): # is object
			text = object_replace(replacer,text)
			#print('obj')
		else:
			if isinstance(replacer[0], str): # is string
				replacement = strip_duplicate_groups(replacer[0])
				
				#print('repl ', replacement)
				#print('repl1 ', replacer[1])
				#print('t ', text)
				text = regex.sub(replacement, replacer[1], text,0,flags)
				
				#print('str ', replacer[1])
			elif isinstance(replacer[0],list): # Is array
				text = array_replace(replacer[0],replacer[1],text)
				#print('list')
			else:
				print("ERROR")

		if not repeat:
			break;
		#print('continue ', repeat, replacer);
		if text == prev_text: # Repeatedly apply same operation until no more changes occur.
			break;
		if len(text) > (len(orig_text) * 10 + 1000):
			print(replacer)
			print("SIZE GREW 10x, PRESUMED INFINITE BLOAT, ABORTING!")
			print(text)
			quit();
			break;


	return text

# Convert file from gd to cs
def transpile(filename,outname):
	# Open the file in read/write mode
	with open(filename,'r+') as f:
		text = f.read()
		
		print("PROCESSING -- " + filename)

		

		extending = regex.findall(r"extends (.*)\n",text);
		if extending :
			extending = extending[0]
		else:
			extending = "Godot.Object"
		tool = len(regex.findall(r"^@?tool.*$",text,flags)) > 0


		for pair in function_replacements:
			pair[0] = fr"(?<={separator})(?<![.])" + pair[0] + fr"(?=\()";
			text = regex.sub(pair[0], pair[1], text,0,flags)


		for pair in replacements:
			text = _try_replace(text,pair)

		if refactor_onready:
			onready_code_prepend = ["{"]
			matches = regex.findall(fr"{match_field_declaration}\s*(=.*)$",text,flags)
			for match in matches:
				prefixes = match[3]
				if not "onready" in prefixes:
					continue
				onready_code_prepend.append("\t"+match[15] + " " + match[28])

			#print("Tryign replacement", onready_code_prepend)
			# Check if _Ready or _ready exists

			
			if(0 >= len(regex.findall(fr"public void _[rR]eady\s*\(\s*\)",text))): # Insert a _Ready function if it doesn't exist yet.
				text = "public void _Ready()\n{\t\n}\n\n" + text

			# Insert all assignments into Ready function
			text = _try_replace(text,
			{ 
				"repeat":False,
				"match":fr"public void _[rR]eady\s*\(\s*\)\s*(?P<Content>{match_curlies})",
				"children":{
					"Content":[
					{
						"repeat":False,
						"replacement":[fr"{{",str.join("\n",onready_code_prepend)],
						#"replacement_f":lambda a,b : print(a) or a
					}
				],
				},
				#"replacement_f":lambda a,b : print(a) or a
			}
			)
			
			# TODO : Remove assignments from onready field declarations
			print(regex.findall(fr"\sonready\s(.*)=.*;",text))
			text = regex.sub(fr"\sonready\s(.*)=.*;",fr" \1;",text)


			# next, remove onready keyword everywhere
			#text = regex.sub(fr"(?<={separator})onready\s","",text)
			

			#text = _try_replace(text,)

		
		

		text = regex.sub("^","\t",text,0,flags); # Offset all the code by 1 tab, ready to be surrounded by class{...}

		print(outname)
		class_name = regex.findall(fr"([^/]*)(?=\.cs)",outname,flags)[0];
		print(class_name)
		text = f"{header}\n{'[Tool]' if tool else ''}\npublic class {class_name} : {extending}\n{{\n" + text + "\n}";
		with open(outname,'w') as wf:
			wf.write(text);
			print("SUCCESS -- " + outname)


"""