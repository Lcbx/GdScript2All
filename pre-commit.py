print("regenerating README")

def read_file(filename):
	with open(filename, 'r') as f:
		return f.read()

template = read_file('README_TEMPLATE.md')

testGd = read_file('tests/test.gd')
testCs = read_file('results/test.cs')

newReadme = template \
	.replace('__test.gd__', testGd) \
	.replace('__test.cs__', testCs)
# TODO : add cpp transpilation results

with open('README.md', 'w+') as f: f.write(newReadme)

# add the change to the commit
import subprocess
subprocess.run(['git', 'add', 'README.md'])