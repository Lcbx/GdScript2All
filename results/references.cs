using System;
using Godot;
using Dictionary = Godot.Collections.Dictionary;
using Array = Godot.Collections.Array;


public partial class references : Godot.Node
{
	public Godot.Variant Variable = Foo;
	public Godot.Variant Reference = Foo.Bar;
	public Godot.Variant Function = Foo();
	public Godot.Variant FunctionParams = Foo(a, b);
	public Godot.Variant Method = Foo.Bar();
	public Godot.Variant FunctionMethodParams = Foo(a, b).Bar(c, d);
	public Godot.Variant RefMethod = Foo.Bar.Baz();
	public Godot.Variant MethodRef = Foo.Bar().Baz;
	public Godot.Variant Subscription = this.Dict[0];
}