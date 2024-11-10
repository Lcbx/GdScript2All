import os
import sys
from subprocess import run

def main():
	
	import argparse
	commandLineArgs = argparse.ArgumentParser(description='GDscript transpiler')
	commandLineArgs.add_argument('input', nargs = '*', help='path to GDscript code (folder or file)', default = ['./tests'])
	commandLineArgs.add_argument('-o', '--output', nargs = '?', default = './results', help='where to output transpiled code ')
	commandLineArgs.add_argument('-t', '--transpiler', nargs = '?', default = 'CSharp', help='which transpiler script to use')
	commandLineArgs.add_argument('-v', '--verbose', action='store_true', default = False, help='print additional execution logs' )
	commandLineArgs.add_argument('--use_floats', action='store_true', default = False, help='leave floating point types as floats' )
	commandLineArgs.add_argument('--transpiler_verbose', action='store_true', default = False, help='print additional parser execution logs' )
	commandLineArgs.add_argument('--parser_verbose', action='store_true', default = False, help='print additional transpiler execution logs' )
	commandLineArgs.add_argument('--no_type_resolving', action='store_true', default = False, help='removes the initial type resolving step for user types' )
	commandLineArgs.add_argument('--no_save', action='store_true', default = False, help='do not save output code as a file' )
	commandLineArgs.add_argument('--print_tokens', action='store_true', default = False, help='print the tokenizer output' )
	commandLineArgs.add_argument('--log_file', default = '', help='redirect stdout and stderr to specified filepath' )
	commandLineArgs.add_argument('--create_gdextension', default = '', help='creates a gdextension cpp project in the output dir with specified name' )
	args = commandLineArgs.parse_args()
	
	import src
	import Parser
	from UserTypesResolver import Transpiler as TypeResolver

	if args.log_file: sys.stdout = sys.stderr = open(args.log_file, 'w')

	# dynamic import
	Transpiler = __import__(args.transpiler.replace('.py', ''))
	Transpiler.use_floats = args.use_floats

	# for verbose printing
	def getPrinter(condition): return print if condition else lambda a,*b:None

	# files to transpile
	input_files = set()
	args.output = os.path.normpath(args.output)
	for path in map(os.path.normpath, args.input):
		if os.path.isdir(path):
			# Find all gd files in input dir
			input_files.update([
				os.path.join(root, file)
				for root, dirs, files in os.walk(path)
				for file in files
				if os.path.splitext(file)[1] == '.gd'
			])
		else:
			# simple file
			input_files.add( path )

	if args.verbose:
		print(f"args: {sys.argv}")
		print(f"files to process :\n{input_files}")

	total = len(input_files)


	# script name without extension
	to_script_name = lambda s: os.path.basename(s).split('.')[0]
	# dir/script name
	to_simple_path = lambda s: ( \
		f'{split_path[-2]}/{os.path.basename(s)}' if len(split_path := s.split(os.path.sep)) > 1 \
		else os.path.basename(s))

	# type resolving step : useful for both calling user classes from another
	# and for using method result type before it is defined  
	script_classes = {}
	failed = False
	if not args.no_type_resolving:
		for i, filename in enumerate(input_files):
			try:
				with open(filename,'r+') as f: text = f.read()
				parser = Parser.Parser(to_script_name(filename), text, TypeResolver(), lambda a,*b:None )
				parser.transpile()
				script_classes[parser.getClassName()] = parser.getClass()
				
			except Exception as ex:
				handleException(parser, ex)
				failed = True

		if failed: return

		# we add the deduced types the parser class,
		# they'll be available in the actual transpiling step
		Parser.godot_types.update(script_classes)

	# generate the cpp project if specified
	if project_name := args.create_gdextension:
		generate_project(args.output, project_name, script_classes.keys())

	for i, filename in enumerate(input_files):
		try:
			
			filedir = os.path.dirname(filename)
			outname = (filename.replace(filedir, args.output) if filedir else os.path.join(args.output, filename) ).replace('.gd', '')
			os.makedirs(os.path.dirname(outname), exist_ok=True)
			
			with open(filename,'r+') as f: text = f.read()
			
			script_name = to_script_name(filename)
			transpiler = Transpiler.Transpiler(script_name, outname, getPrinter(args.verbose or args.transpiler_verbose) )
			parser = Parser.Parser(script_name, text, transpiler, getPrinter(args.verbose or args.parser_verbose) )
			
			if args.print_tokens:
				print('\n'.join(map(lambda token: f'line {token.lineno}: {token.type} <{token.value}>', parser.tokenizer.tokenize(text))))
		
			parser.transpile()
			
		except Exception as ex:
			handleException(parser, ex)
			
		if not args.no_save:
			transpiler.save_result()

		print(f"Converted {to_simple_path(filename)} to {to_simple_path(outname)} ({i+1}/{total})")


def handleException(parser, ex):
		print('parser fail on', parser.current)
		
		ex_msg = str(ex); ex_msg = ex_msg if ex_msg != 'None' else ''
		ex_type = type(ex).__name__
		tb = ex.__traceback__

		print(f'\033[91m{ex_type} {ex_msg}\033[0m')
		while tb != None:
			filename = os.path.split(tb.tb_frame.f_code.co_filename)[1]
			lineno = tb.tb_lineno
			name = tb.tb_frame.f_code.co_name
			print(f'  at {filename}:{lineno}\t{name}')
			tb = tb.tb_next

def generate_project(base_path, project_name : str, classes : list) -> None:
	project_path = os.path.join(base_path, project_name)

	# official template
	TEMPLATE_URL = 'https://github.com/godotengine/godot-cpp-template'

	# dowload the official template project
	run(['git', 'clone', f'{TEMPLATE_URL}.git', project_path])

	# go into created project dir
	os.chdir(project_path)

	# setup godot-cpp
	run(['git', 'submodule', 'update', '--init'])

	# Overwrite the old main branch reference with the new one
	run(['git', 'checkout', '--orphan', 'new-main', 'main'])
	run(['git', 'commit', '-m', f'"initial commit based on {TEMPLATE_URL}"'])
	run(['git', 'branch', '-M', 'new-main', 'main'])

	# NOTE: following manipulations need to be kept up to date
	# with template's dir structure and file contents

	init = { 'example_library_init':f'{project_name}_init' }
	register_classes = { '//ClassDB::register_class<YourClass>();':
		'\n\t'.join(map(lambda c: f'ClassDB::register_class<{c}>();', classes))
	}
	file_replace('SConstruct', {'EXTENSION-NAME':project_name,
		# temporary fix
		'env.InstallAs("{}/bin/{}/lib{}".format(projectdir, env["platform"], file), library)':'env.InstallAs("{}/bin/lib{}".format(projectdir, file), library)'
	})
	file_replace('src/register_types.h', {'EXAMPLE_REGISTER_TYPES_H':f'{project_name.upper()}_REGISTER_TYPES_H'})
	file_replace('src/register_types.cpp', {**init, **register_classes})
	file_replace('demo/bin/example.gdextension', {**init, 'gdexample':project_name})
	os.rename('demo/bin/example.gdextension', f'demo/bin/{project_name}.gdextension')
	
	# go back
	os.chdir('../..')

def file_replace(file_name, changes_dict : dict):
    with open(file_name, "r+") as file:
        contents = file.read()
        for old, new in changes_dict.items():
        	contents = contents.replace(old, new)

        file.seek(0)
        file.write(contents)
        file.truncate()

if __name__ == '__main__':
	main()
