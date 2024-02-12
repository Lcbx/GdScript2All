## GdScript2All
A python tool for migrating GdScript to C# currently and eventually cpp with features like type inference (see example).

### Usage
```bash
py main.py -i <file_or_folder_path> -o <output_file_or_folder_path>
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

### Limitations
- read [TODO.md](TODO.md) for WIP features
- type inference does not currently support user-defined classes
- pattern matching ex:  
```
match [34, 6]:
  [0, var x]:
     print(x)
  [var y, 6] when y > 10 :
     print(y)
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

