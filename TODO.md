## TODO
- [x] flesh out README.md
- [x] support getset properties
- [x] support signals
- [x] support lambda functions
- [x] detect base class method override (_ready, _process, ...)
- [x] C# : rename methods/properties to Pascal-case ex: "Engine.is_editor_hint" => "Engine.IsEditorHint"
- [ ] lambda return type inference
- [x] export groups/subgroups annotations
- [ ] enum as a type, ex: "var v = MyEnum.FOO" => "MyEnum v = MyEnum.FOO;"
- [x] await ex: "await" => "await ToSignal(....)
- [x] use argparse instead of hand-parsing sys.argv
- [x] move C# translations out of godot_type.py
- [x] add onready assignments to ready method
- [x] support onreadies in nested classes (rn they get added to script class)
- [x] add c++ transpiling backend
- [x] c++ : generate bindings for methods and exported properties
- [x] c++ : fix duplicated nested class bug (see script-level.hpp) + cleanup Stringbuilder
- [x] c++ : lambda creation 
- [ ] c++ : use double instead of float
- [ ] c++ : use Ref<> instead of *
- [ ] c++ : add missing get when there is a set (not sure about the inverse) 
- [ ] c++ : typed array needs special binding (see https://forum.godotengine.org/t/how-to-set-up-a-typedarray-with-a-custom-type-in-gdextension/37652/3)
- [ ] c++ : add ; after class
- [ ] c++ : bind overloaded methods
- [ ] c++ : automatic includes based on member types
- [ ] c++ : move static member initilisation into cpp
- [ ] c++ : better enum support (enum.value => class::enum::value)
- [ ] c++ : bind enums : 'VARIANT_ENUM_CAST in bindings + BIND_ENUM_CONSTANT in hpp after class
- [ ] c++ : move property initalization to a constructor ?
- [ ] use gdextension dump json ('godot --dump-extension-api') instead of parsing docs
  * contains cpp class header structure (ex: "classes/timer.hpp")
  * better enum support
- [ ] support user-defined classes in type inference
- [ ] special literals :
  * floating exponents : 58e-10
  * base16 int : 0x8E
  * binary int : 0b1010
  * raw strings : r"hello"
  * string names : &"name"
  * nodepath : ^"parent/child"