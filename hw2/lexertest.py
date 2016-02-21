import decaflexer
import sys
import ply.lex as lex

lexer = lex.lex(module=decaflexer)
lexer.input(sys.stdin.read())

while True:
	token = lexer.token()
	if not token:
		break
	print(token)