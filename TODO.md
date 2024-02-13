## TODO
- [x] flesh out README.md
- [ ] support getset properties
- [x] support signals
- [ ] detect base class method override (_ready, _process, ...)
- [ ] await <expr> => await ToSignal(<expr>)
- [ ] use argparse instead of hand-parsing sys.argv
- [ ] move C# translations out of godot_type.py
- [ ] add onready assignments to ready method
- [ ] add c++ transpiling backend
- [ ] c++ : generate bindings for methods and exported properties
- [ ] support enum as a variable type, ex: "var v = MyEnum.FOO" => "MyEnum v = MyEnum.FOO;"
- [ ] support using user-defined classes in other user scripts
- [ ] support await ex: "await" => "await ToSignal(....)
- [ ] C# : rename methods/properties to Pascal-case ex: "Engine.is_editor_hint" => "Engine.IsEditorHint"
- [ ] support special literals :
  * floating exponents : 58e-10
  * base16 int : 0x8E
  * bineary int : 0b1010
  * raw strings : r"hello"
  * string names : &"name"
  * nodepath : ^"parent/child"