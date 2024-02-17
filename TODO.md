## TODO
- [x] flesh out README.md
- [x] support getset properties
- [x] support signals
- [ ] detect base class method override (_ready, _process, ...)
- [x] support await ex: "await" => "await ToSignal(....)
- [x] use argparse instead of hand-parsing sys.argv
- [ ] move C# translations out of godot_type.py
- [x] add onready assignments to ready method
- [ ] add c++ transpiling backend
- [ ] c++ : generate bindings for methods and exported properties
- [ ] support enum as a variable type, ex: "var v = MyEnum.FOO" => "MyEnum v = MyEnum.FOO;"
- [ ] support user-defined classes in type inference
- [ ] C# : rename methods/properties to Pascal-case ex: "Engine.is_editor_hint" => "Engine.IsEditorHint"
- [ ] support special literals :
  * floating exponents : 58e-10
  * base16 int : 0x8E
  * binary int : 0b1010
  * raw strings : r"hello"
  * string names : &"name"
  * nodepath : ^"parent/child"