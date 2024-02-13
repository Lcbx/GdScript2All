using System;
using Godot;
using Dictionary = Godot.Collections.Dictionary;
using Array = Godot.Collections.Array;


// basic expressions
public partial class expressions : Godot.Node
{
	public Godot.Variant foo;
	public static int i = 0;
	public const string str = "the fox said \"get off my lawn\"";
	public string big_str = @"
	this is a multiline string
	";
	protected bool _protected_bool = true;
	public Array array = new Array{0,1,2,};
	public Dictionary dict = new Dictionary{{0,1},{1,2},{2,3},};
	public Array<string> string_array = new Array{"0","1",};
	public int parenthesis = (42);
	public int delayed_expression = 1;
	public double asKeyword = 3;
	
	// multi-part expressions
	public double arithmetic =  - j * 0.5;
	public bool comparison = arithmetic >= 0.5 && arithmetic == 6.0;
	public Godot.Variant ternary = ( true ? cond_true : cond_false );
	public int nested_ternary = ( cond1 && 5 > 6 ? cond1_true * 3 : ( cond2 || (7 < 0) ? cond2_true | 4 : cond12_false && 0 ) );
	
	
	
}