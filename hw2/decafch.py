from __future__ import print_function
import sys
import ply.yacc as yacc
import ply.lex as lex

import decaflexer
import decafparser

if __name__ == '__main__':
	if len(sys.argv) != 2:
		print("usage: python decafch.py <file>")
		sys.exit(1)

	with open(sys.argv[1]) as f:
		data = f.read()
		lexer = lex.lex(module=decaflexer)
		parser = yacc.yacc(module=decafparser)
		parser.parse(data)

		# Parse successful
		print ("Parse successful!")
