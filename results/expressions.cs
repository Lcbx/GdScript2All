using System;
using Godot;
using Dictionary = Godot.Collections.Dictionary;
using Array = Godot.Collections.Array;


// basic expressions
public partial class expressions : Godot.Node
{
	public Godot.Variant Foo;
	public static int I = 0;
	public const string STR = "the fox said \"get off my lawn\"";
	public string BigStr = @"
	this is a multiline string
	";
	protected bool _ProtectedBool = true;
	public Array Array = new Array{0,1,2,};
	public Dictionary Dict = new Dictionary{{0,1},{1,2},{2,3},};
	public Array<string> StringArray = new Array{"0","1",};
	public int Parenthesis = (42);
	public int DelayedExpression = 1;
	public double AsKeyword = 3;
	
	// multi-part expressions
	public double Arithmetic =  - j * 0.5;
	public bool Comparison = Arithmetic >= 0.5 && Arithmetic == 6.0;
	public Godot.Variant Ternary = ( true ? cond_true : cond_false );
	public int NestedTernary = ( cond1 && 5 > 6 ? cond1_true * 3 : ( cond2 || (7 < 0) ? cond2_true | 4 : cond12_false && 0 ) );
	
	
	
}