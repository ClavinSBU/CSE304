decaflexer.py:
	decaflexer contains the token specifications for PLY/lex. Per the CSE304 specification, it does not support string constants with escaped double quotes, array syntax, or floating point constants with exponentiation.

decafparser.py:
	decafparser contains the grammar specification for PLY/yacc. Per the CSE304 specification, it does not support array declaration, array expressions, or array creation.

decafch.py:
	decafch is the command-line syntax checker that utilizes the token and grammars specified in decaflexer and decafparser respectively. It takes a file name as an argument and then attempts to parse it. If the syntax is correct, it will print "Parse successful!" If there was an error, it will print what went wrong as well as where in the file it went wrong.