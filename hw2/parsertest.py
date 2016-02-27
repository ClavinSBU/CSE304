import sys
import ply.yacc as yacc
import ply.lex as lex

import decaflexer
import decafparser

lexer = lex.lex(module=decaflexer)

data = sys.stdin.read()

parser = yacc.yacc(module=decafparser)
parser.parse(data,lexer=lexer)

print("Parse successful!")