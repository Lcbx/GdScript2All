import os
import sys

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
	commandLineArgs.add_argument('--print_tokens', action='store_true', default = False, help='if set will print the tokenizer output' )
	args = commandLineArgs.parse_args()
	
	import src
	import Parser
	from UserTypesResolver import Transpiler as TypeResolver

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
	to_simple_path = lambda s: f'{s.split(os.path.sep)[-2]}/{os.path.basename(s)}'

	# type resolving step : useful for both calling user classes from another
	# and for using method result type before it is defined  
	script_classes = {}
	if not args.no_type_resolving:
		for i, filename in enumerate(input_files):
			try:
				with open(filename,'r+') as f: text = f.read()
				parser = Parser.Parser(to_script_name(filename), text, TypeResolver(), lambda a,*b:None )
				parser.transpile()
				script_classes[parser.getClassName()] = parser.getClass()
				
			except Exception as e:
				handleException(e)

		# we add the dduces types the parser class,
		# they'll be available in the actual trnaspiling step
		Parser.godot_types.update(script_classes)

	for i, filename in enumerate(input_files):
		try:
		
			outname = filename.replace(os.path.dirname(filename), args.output).replace('.gd', '')
			os.makedirs(os.path.dirname(outname), exist_ok=True)
			
			with open(filename,'r+') as f: text = f.read()
			
			script_name = to_script_name(filename)
			transpiler = Transpiler.Transpiler(script_name, outname, getPrinter(args.verbose or args.transpiler_verbose) )
			parser = Parser.Parser(script_name, text, transpiler, getPrinter(args.verbose or args.parser_verbose) )
			
			if args.print_tokens:
				print('\n'.join(map(lambda token: f'line {token.lineno}: {token.type} <{token.value}>', parser.tokenizer.tokenize(text))))
		
			parser.transpile()
			
		except Exception as e:
			handleException(e)
			
		if not args.no_save:
			transpiler.save_result()

		print(f"Converted {to_simple_path(filename)} to {to_simple_path(outname)} ({i+1}/{total})")

def handleException(e):
		ex_msg = str(e); ex_msg = ex_msg if ex_msg != 'None' else ''
		ex_type = type(e).__name__
		tb = e.__traceback__

		print(f'\033[91m{ex_type} {ex_msg}\033[0m')
		while tb != None:
			filename = os.path.split(tb.tb_frame.f_code.co_filename)[1]
			lineno = tb.tb_lineno
			name = tb.tb_frame.f_code.co_name
			print(f'  at {filename}:{lineno}\t{name}')
			tb = tb.tb_next

if __name__ == '__main__':
	main()