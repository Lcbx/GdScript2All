## TODO
- [ ] move TODOs to github issues
- [x] detect base class method override (_ready, _process, ...)
- [x] C# : rename methods/properties to Pascal-case ex: "Engine.is_editor_hint" => "Engine.IsEditorHint"
- [ ] lambda return type inference
- [x] export groups/subgroups annotations
- [x] enum as a type, ex: "var v = MyEnum.FOO" => "MyEnum v = MyEnum.FOO;"
- [x] await ex: "await" => "await ToSignal(....)
- [x] add onready assignments to ready method
- [x] c++ : generate bindings for methods and exported properties
- [x] c++ : add missing get/set when there is one defined 
- [ ] c++ : typed array needs special binding (see https://forum.godotengine.org/t/how-to-set-up-a-typedarray-with-a-custom-type-in-gdextension/37652/3)
- [x] c++ : add bindings for overloaded methods
- [x] c++ : automatic includes based on member types
- [x] c++ : move static member initilisation into cpp
- [x] c++ : better enum support (enum.value => class::enum::value)
- [x] c++ : bind enums
- [ ] c++ : fix unamed enums having empty binding call (```VARIANT_ENUM_CAST()```)
- [ ] c++ : move property initalization to a constructor ?  
- [ ] <del>use gdextension dump json ('godot --dump-extension-api') instead of parsing docs</del>  
      has some problems, see switchToExtensionDump branch
- [x] support user-defined classes in type inference
- [x] add a setting for double or float as default floating point data type
- [ ] special literals :
  * floating exponents : 58e-10
  * <del>base16 int : 0x8E</del> (done)
  * binary int : 0b1010
  * raw strings : r"hello"
  * string names : &"name"
  * nodepath : ^"parent/child"
