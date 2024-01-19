import os
import sys

import godotReference as ref
import Parser
import CsharpTranspiler


input = "tests"
output = "results"
files = []

# Read console arguments
if len(sys.argv):
	i = 0
	while i < len(sys.argv):
		arg = sys.argv[i]
		if arg == "-f" or arg == "-i":
			input = sys.argv[i+1]
			i+=2
		elif arg == "-o":
			output = sys.argv[i+1]
			i+=2
		else:
			print(f"Unknown argument : '{sys.argv[i]}'")
			i+=1


if os.path.isdir(input):
	# Find all gd files in input dir
	files = [
		os.path.join(root, file)
		for root, dirs, files in os.walk(input)
		for file in files
		if os.path.splitext(file)[1] == '.gd'
	]
else:
	files = [input]

print(f"files to process :\n{files}")

def transpile(filename, outname):
	# Open the file in read/write mode
	with open(filename,'r+') as f:
		text = f.read()
		
	print("PROCESSING -- " + filename)
	
	transpiler = CsharpTranspiler.CSharpTranspiler()
	
	parser = Parser.Parser(text, transpiler)
	#print(transpiler.tokens)
	
	parser.transpile()

	print(outname)
	text = transpiler.text
	with open(outname,'w+') as wf:
		wf.write(text);
		print("SUCCESS -- " + outname)


total = len(files)
for i, file in enumerate(files):
	outname = file.replace(input, output).replace('.gd', '')
	outname = outname + '.cs' if not outname.endswith('.cs') else outname
	transpile(file, outname)
	print(f"Converted {file} to {outname} ({i+1}/{total})")