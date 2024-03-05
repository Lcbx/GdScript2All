print("regenerating README")
import subprocess

def read_file(filename):
	with open(filename, 'r') as f:
		return f.read()

# transpile the test code
subprocess.run(['py', 'main.py'])
subprocess.run(['py', 'main.py', '-t', 'Cpp'])

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

# add the change to the commit
subprocess.run(['git', 'add', 'README.md'])

# show files commited
subprocess.run(['git', 'status'])