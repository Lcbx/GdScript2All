print("regenerating README")
from subprocess import run

def read_file(filename):
	with open(filename, 'r') as f:
		return f.read()

# transpile the test code
mainPath = 'addons/gdscript2all/converter/main.py'
run(['python', mainPath])
run(['python', mainPath, '-t', 'Cpp'])

template = read_file('README_TEMPLATE.md')

transforms = {
	# original
	'__test.gd__': 'tests/test.gd',
	# conversions
	'__test.cs__': 'results/test.cs',
	'__test.hpp__': 'results/test.hpp',
	'__test.cpp__': 'results/test.cpp',
}

newReadme = template 


for placeholder, filename in transforms.items():
	newReadme = newReadme.replace(placeholder, read_file(filename) \
		.replace('\t', '    ')) # github tabs are huge

with open('README.md', 'w+') as f: f.write(newReadme)

# keep files in addon updated
run(['cp', 'LICENSE',   'addons/gdscript2all/'])
run(['cp', 'README.md', 'addons/gdscript2all/'])

# add the change to the commit
run(['git', 'add', 'README.md'])
run(['git', 'add', 'addons/gdscript2all/README.md'])

# show files commited
run(['git', 'status'])