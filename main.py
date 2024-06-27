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
	commandLineArgs.add_argument('--verboseP', action='store_true', default = False, help='print additional parser execution logs' )
	commandLineArgs.add_argument('--verboseT', action='store_true', default = False, help='print additional transpiler execution logs' )
	commandLineArgs.add_argument('--no_type_resolving', action='store_true', default = False, help='removes the initial type resolving step for user types' )
	commandLineArgs.add_argument('--no_save', action='store_true', default = False, help='do not save output code as a file' )
	commandLineArgs.add_argument('--tokens', action='store_true', default = False, help='if set will print the tokenizer output' )
	args = commandLineArgs.parse_args()
	
	import src
	import Parser
	from UserTypesResolver import Transpiler as TypeResolver

	# dynamic import
	Transpiler = __import__(args.transpiler.replace('.py', ''))

	# for verbose printing
	def getPrinter(condition): return print if condition else lambda a,*b:None

	# files to transpile
	input_files = set()
	for path in args.input:
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

	script_classes = {}

	# script name without extension
	to_script_name = lambda s: os.path.basename(s).split('.')[0]

	# type resolving step : useful for both calling user classes from another
	# and for using method result type before it is defined  
	if not args.no_type_resolving:
		for i, filename in enumerate(input_files):

			with open(filename,'r+') as f:
				text = f.read()

			# script name without extension
			script_name = to_script_name(filename)

			transpiler = TypeResolver()
			parser = Parser.Parser(script_name, text, transpiler, lambda a,*b:None )

			try:
				parser.transpile()
				script_classes[parser.getClassName()] = parser.getClass()
				#print('done', filename, script_classes.keys())
				
			except Exception as e:
				handleException(e)

		Parser.godot_types.update(script_classes)

	for i, filename in enumerate(input_files):
		
		outname = filename.replace(os.path.dirname(filename), args.output).replace('.gd', '')
		os.makedirs(os.path.dirname(outname), exist_ok=True)
		
		with open(filename,'r+') as f:
			text = f.read()
		
		script_name = to_script_name(filename)
		
		Transpiler.use_floats = args.use_floats
		transpiler = Transpiler.Transpiler(script_name, outname, getPrinter(args.verbose or args.verboseT) )
		
		parser = Parser.Parser(script_name, text, transpiler, getPrinter(args.verbose or args.verboseP) )
		
		if args.tokens:
			print(outname)
			print('\n'.join(map(lambda token: f'line {token.lineno}: {token.type} <{token.value}>', parser.tokenizer.tokenize(text))))
		
		printException = lambda : None
		
		try:
			parser.transpile()
			
		except Exception as e:
			handleException(e)
			
		if not args.no_save:
			transpiler.save_result()
		
		print(f"Converted {filename} to {outname} ({i+1}/{total})")

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