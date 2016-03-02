from __future__ import print_function
from sys import exit

reserved = {
    'boolean': 'BOOLEAN',
    'break': 'BREAK',
    'continue': 'CONTINUE',
    'class': 'CLASS',
    'do': 'DO',
    'else': 'ELSE',
    'extends': 'EXTENDS',
    'false': 'FALSE',
    'float': 'FLOAT',
    'for': 'FOR',
    'if': 'IF',
    'int': 'INT',
    'new': 'NEW',
    'null': 'NULL',
    'private': 'PRIVATE',
    'public': 'PUBLIC',
    'return': 'RETURN',
    'static': 'STATIC',
    'super': 'SUPER',
    'this': 'THIS',
    'true': 'TRUE',
    'void': 'VOID',
    'while': 'WHILE'
}

tokens = [
    # Identifiers and Constants
    'ID', 'INTCONST', 'FLOATCONST', 'STRINGCONST',
    # Arithmetic Ops + - * /
    'PLUS', 'MINUS', 'MULT', 'DIV',
    # Boolean Ops ! && || == != < > <= >=
    'NOT', 'AND', 'OR', 'EQ', 'NE', 'LT', 'GT', 'LTE', 'GTE',
    # Assignment Ops = ++ --
    'EQUALS', 'INC', 'DEC',
    # Symbols ( ) { } ; , .
    'LPAREN', 'RPAREN', 'LBRACE', 'RBRACE',
    'SEMICOLON', 'COMMA', 'DOT'
] + list(reserved.values()) # Add the reserved keywords as tokens

t_INTCONST = r'\d+'
t_FLOATCONST = r'\d+\.\d+'
t_STRINGCONST = r'"[^"]*"'
t_PLUS = r'\+'
t_MINUS = r'-'
t_MULT = r'\*'
t_DIV = r'/'
t_NOT = r'!'
t_AND = r'&&'
t_OR = r'\|\|'
t_EQ = r'=='
t_NE = r'!='
t_LT = r'<'
t_GT = r'>'
t_LTE = r'<='
t_GTE = r'>='
t_EQUALS = r'='
t_INC = r'\+\+'
t_DEC = r'--'
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_LBRACE = r'\{'
t_RBRACE = r'\}'
t_SEMICOLON = r';'
t_COMMA = r','
t_DOT = r'\.'

t_ignore = " \t" # Ignore whitespace except for newlines

t_ignore_COMMENT = r'//.*'

def t_MULTILINECOMMENT(t):
    r'/\*(.|\n)*?\*/'
    # Must be non-greedy otherwise /**/(code)/**/ doesn't scan (code) properly
    t.lexer.lineno += t.value.count("\n")

# Capture newlines to increment line number
def t_newline(t):
    r'\n+'
    t.lexer.lineno += t.value.count("\n")

def t_ID(t):
    r'[a-zA-Z][a-zA-Z0-9_]*'
    t.type = reserved.get(t.value, 'ID') # Check if reserved keyword
    return t

def t_error(t):
    last_newline = t.lexer.lexdata.rfind('\n', 0, t.lexpos)
    if last_newline < 0:
        last_newline = 0
    next_newline = t.lexer.lexdata.find('\n', t.lexpos)
    column = t.lexpos - last_newline

    print("Illegal character '{0}' found on line {1}, column {2}:".format(
        t.value[0], t.lexer.lineno, column))
    print(t.lexer.lexdata[last_newline+1:next_newline])
    
    print("Exiting now.")
    exit(1)
