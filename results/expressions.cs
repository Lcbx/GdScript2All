using System;
using Godot;
using Godot.Collections;


// basic expressions
[GlobalClass]
public partial class expressions : Godot.Node
{
	public Godot.Variant Foo;
	public static int I = 0;
	public const string Str = "the fox said \"get off my lawn\"";
	public String BigStr = @"
	this is a multiline string
";
	protected bool _ProtectedBool = true;
	public Array Array = new Array{0, 1, 2, };
	public Dictionary Dict = new Dictionary{{0, 1},{1, 2},{2, 3},};
	public Array<String> StringArray = new Array{"0", "1", };
	public int Parenthesis = (42);
	public int DelayedExpression = 1;
	public double AsKeyword = 3;
	public Array<Animation.TrackType> ArrayOfEnum;
	public double FuncCall = Mathf.Sin(34);
	// comment \
	public double FuncDelayed = Mathf.Exp(1, 2);

	// multi-part expressions
	public double Arithmetic =  - I * 0.5;
	public bool Comparison = Arithmetic >= 0.5 && Arithmetic == 6.0;
	public Godot.Variant Ternary = ( true ? cond_true : cond_false );
	public int NestedTernary = ( cond1 && 5 > 6 ? cond1_true * 3 : ( cond2 || (7 < 0) ? cond2_true | 4 : cond12_false && 0 ) );


}