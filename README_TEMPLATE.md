## GdScript2All
A python tool for migrating [Godot](https://github.com/godotengine/godot)'s GdScript to any languages (C# only currently but eventually c++) with features like type inference.
It should be fairly easy to add new langugages (see [here](#Adding-new-languages))

### Usage
```bash
py main.py <file_or_folder_path> -o <output_file_or_folder_path>
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
c++ output (TODO!) :
```c++
__test.hpp__
```
```c++
__test.cpp__
```

### Adding new languages
If you want to transpile to an unsupported language, rename a copy of the [C# transpiler backend](src/CsharpTranspiler.py),
modify it as needed, then to use it you just have to pass its name with the ```-t``` flag:
```bash
py main.py -t CustomTranspiler <file_or_folder_path>
```

### Limitations
- read [TODO.md](TODO.md) for WIP features
- type inference does not currently support user-defined classes
- pattern matching ex:  
```GDScript
match [34, 6]:
  [0, var y]:
     print(y)
  [var x, 6] when x > 10 :
     print(x)
```
will probably not be supported (too complicated to generate an equivalent)

### To update the API definition
* clone the offical godot repo
* copy it's ```doc/classes``` folder and paste it into our ```classData``` folder
* install untangle (xml parsing library) if you don't have it (```pip install untangle```)
* run ```py src/godot_types.py``` to generate the pickle class db
* profit.

### Explaining the GPL-3.0 license
The code this tool generates from your GDScipt is yours.
However, any modifications made to this tool's source has to be available to the open-source community.
I think that is a fair deal.
  
<a href="https://www.buymeacoffee.com/Lcbx" target="_blank"><img src="https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png" alt="Buy Me A Coffee" style="box-shadow: 0px 3px 2px 0px rgba(190, 190, 190, 0.5) !important;-webkit-box-shadow: 0px 3px 2px 0px rgba(190, 190, 190, 0.5) !important;" ></a>

