using Godot;
using Godot.Collections;


// basic expressions
[GlobalClass]
public partial class expressions : Godot.Node
{
	public Godot.Variant Foo;
	public int Orignal;
	public static int I = 0;
	public const string Str = "the fox said \"get off my lawn\"";
	public String BigStr = @"
	this is a multiline string
";
	public string EscapedStr = "\n \\ \" ";
	protected bool _ProtectedBool = true;
	public Array Array = new Array{0, 1, 2, };
	public bool HasCall = Array.Contains(3);
	public Dictionary Dict = new Dictionary{{0, 1},{1, 2},{2, 3},};
	public Array<String> StringArray = new Array{"0", "1", };
	public Dictionary<String,int> TypedDict = new Dictionary{};
	public int Parenthesis = (42);
	public int DelayedExpression = 1;
	public double AsKeyword = 3;
	public Array<Animation.TrackType> ArrayOfEnum;
	public double FuncCall = Mathf.Sin(34);

	// comment \
	public double FuncDelayed = Mathf.Exp(1, 2);

	public Godot.Variant DictSubscription = Dict[0];
	public int TypedDictSubscription = TypedDict["0"];


	// multi-part expressions
	public double Arithmetic =  - I * 0.5;
	public bool Comparison = Arithmetic >= 0.5 && Arithmetic == 6.0;
	public Godot.Variant Ternary = ( true ? cond_true : cond_false );
	public int NestedTernary = ( cond1 && 5 > 6 ? cond1_true * 3 : ( cond2 || (7 < 0) ? cond2_true | 4 : cond12_false && 0 ) );


	// hexadecimal
	public int Byte = (bytes[6] & 0x0f) | 0x40;


	// and a comment
	public bool Multiline = (_terminal_pad.Length() && (!buffer_size || (_terminal_buffer[ - 1] != _terminal_pad)));

}