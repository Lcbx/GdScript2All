import os
import sys

# allow using scripts in src folder
sys.path.insert(0,'src')

import Parser as Parser
import CsharpTranspiler as CsharpTranspiler

import argparse
commandLineArgs = argparse.ArgumentParser(description='GDscript transpiler')
commandLineArgs.add_argument('input', nargs = '?',  help='path to GDscript code (folder or file)', default = './tests')
commandLineArgs.add_argument('-o', '--output', nargs = '?', default = './results', help='where to output transpiled code ')
commandLineArgs.add_argument('-t', '--transpiler', nargs = '?', default = 'CsharpTranspiler', help='which transpiler script to use')
commandLineArgs.add_argument('-v', '--verbose', action='store_true', default = False, help='print additional execution logs' )
commandLineArgs.add_argument('--verboseP', action='store_true', default = False, help='print additional parser execution logs' )
commandLineArgs.add_argument('--verboseT', action='store_true', default = False, help='print additional transpiler execution logs' )
commandLineArgs.add_argument('--tokens', action='store_true', default = False, help='if set will print the tokenizer output' )
args = commandLineArgs.parse_args()

# dynamic import
Transpiler = __import__(args.transpiler)

# for verbose printing
def getPrinter(condition): return print if condition else lambda a,*b:None

# files to transpile
files = []

if os.path.isdir(args.input):
	# Find all gd files in input dir
	files = [
		os.path.join(root, file)
		for root, dirs, files in os.walk(args.input)
		for file in files
		if os.path.splitext(file)[1] == '.gd'
	]
else:
	files = [args.input]


def transpile(filename, outname):
	with open(filename,'r+') as f:
		text = f.read()
	
	# script name without extension
	script_name = os.path.basename(filename).split('.')[0]
	
	transpiler = Transpiler.Transpiler( getPrinter(args.verbose or args.verboseT) )
	
	parser = Parser.Parser(script_name, text, transpiler, getPrinter(args.verbose or args.verboseP) )
	
	if args.tokens:
		print(outname)
		print('\n'.join(map(lambda token: f'line {token.lineno}: {token.type} <{token.value}>', parser.tokenizer.tokenize(text))))
	
	printException = lambda : None
	
	try:
		parser.transpile()
		
	except Exception as e:
		exceptionStr = str(e)
		def printException(): print(exceptionStr)
	
	finally:
		code = transpiler.get_result()
		if args.verbose:
			print("")
			print("****************  generated code  ****************")
			print(code.replace('\t', '_ '))
			print("**************************************************")
		
		printException()
		
		transpiler.save_result(outname)


if args.verbose:
	print("")
	print(f"files to process :\n{files}")

total = len(files)
for i, file in enumerate(files):
	
	outname = file.replace(args.input, args.output).replace('.gd', '')
	
	transpile(file, outname)
	
	print(f"Converted {file} to {outname} ({i+1}/{total})")