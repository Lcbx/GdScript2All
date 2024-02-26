using System;
using Godot;
using Dictionary = Godot.Collections.Dictionary;
using Array = Godot.Collections.Array;


public partial class references : Godot.Node
{
	public Godot.Variant Variable = foo;
	public Godot.Variant Reference = foo.Bar;
	public Godot.Variant Function = Foo();
	public Godot.Variant FunctionParams = Foo(a, b);
	public Godot.Variant Method = foo.Bar();
	public Godot.Variant FunctionMethodParams = Foo(a, b).Bar(c, d);
	public Godot.Variant RefMethod = foo.Bar.Baz();
	public Godot.Variant MethodRef = foo.Bar().Baz;
	public Godot.Variant Subscription = this.dict[0];
}