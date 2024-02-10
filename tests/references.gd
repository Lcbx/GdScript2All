extends Node

var variable = foo
var reference = foo.bar
var function = foo()
var functionParams = foo(a,b)
var method = foo.bar()
var functionMethodParams = foo(a,b).bar(c,d)
var refMethod = foo.bar.baz()
var methodRef = foo.bar().baz
var subscription = self.dict[0]