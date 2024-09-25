## GdScript2All
A tool for converting [Godot](https://github.com/godotengine/godot)'s GdScript to other languages (currently C# and c++) with features like type inference, written in Python.

#### Editor addon
Not yet available in the Godot asset library. Requires Python 3.9+.  
Download this repo as zip (Code->Download as zip), extract it in your project then enable it in Project Settings->Plugins.
<img style='height: 95%; width: 95%;' src="Screenshot.png">


#### From the command line
call the main script using your favorite command line utility (add ```-t Cpp``` for c++) :
```bash
python addons/gd2all/converter/main.py <file_or_folder_path> -o <output_file_or_folder_path>
```

### Example
script input :
```GDScript
__test.gd__
```
C# output :
```cs
__test.cs__
```
c++ output (header) :
```c++
__test.hpp__
```
c++ output (implementation) :
```c++
__test.cpp__
```

### Adding new languages
If you want to transpile to an unsupported language, rename a copy of the [C# transpiler backend](src/CsharpTranspiler.py),
modify it as needed, then to use it you just have to pass its name with the ```-t``` flag (example below with c++ transpiler):
```bash
python main.py -t Cpp <file_or_folder_path>
```

### Limitations
- generated code might need corrections ! (indentation might need a second pass too)
- this tool parses and emits code ; if it encounters something unexpected it will drop the current line and try to resume at the next (panic mode)
- generated C++ does a best guess on what should be a pointer/reference
- in c++ accessing/modifying parent class properties does not use getters/setters (this is a conscious choice)
- read [TODO.md](TODO.md) for current/missing features
- pattern matching ex:  
```GDScript
match [34, 6]:
  [0, var y]:
     print(y)
  [var x, 6] when x > 10 :
     print(x)
```
will probably not be supported (too complicated to generate an equivalent)

### Updating the API definition
* clone the offical godot repo
* copy it's ```doc/classes``` folder and paste it into our ```classData``` folder
* install untangle (xml parsing library) if you don't have it (```pip install untangle```)
* run ```py src/godot_types.py``` to generate the pickle class db
* profit.

### Explaining the GPL-3.0 license
The code this tool generates from your GDScipt is yours.
However, any improvment made to this tool's source has to be contributed back.
I think that's fair.
  
<a href="https://www.buymeacoffee.com/Lcbx" target="_blank"><img src="https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png" alt="Buy Me A Coffee" style="box-shadow: 0px 3px 2px 0px rgba(190, 190, 190, 0.5) !important;-webkit-box-shadow: 0px 3px 2px 0px rgba(190, 190, 190, 0.5) !important;" ></a>

