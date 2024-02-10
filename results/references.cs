using System;
using Godot;
using Dictionary = Godot.Collections.Dictionary;
using Array = Godot.Collections.Array;


public partial class references : Godot.Node
{
	public Godot.Variant variable = foo;
	public Godot.Variant reference = foo.bar;
	public Godot.Variant function = foo();
	public Godot.Variant functionParams = foo(a,b);
	public Godot.Variant method = foo.bar();
	public Godot.Variant functionMethodParams = foo(a,b).bar(c,d);
	public Godot.Variant refMethod = foo.bar.baz();
	public Godot.Variant methodRef = foo.bar().baz;
	public Godot.Variant subscription = this.dict[0];
}