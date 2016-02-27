import ply.yacc as yacc
from sys import exit
from decaflexer import tokens

precedence = ()

def p_prog(p):
	'''program : class program
			   | empty'''
	pass

def p_class(p):
	'''class : class_decl LBRACE class_body_nonempty RBRACE'''
	pass

def p_class_decl(p):
	'''class_decl : CLASS ID EXTENDS ID
				 | CLASS ID'''
	pass

def p_class_body_nonempty(p):
	'''class_body_nonempty : class_body_decl class_body'''
	pass

def p_class_body(p):
	'''class_body : class_body_decl class_body
				  | empty'''
	pass

def p_class_body_decl(p):
	'''class_body_decl : field_decl'''
	pass # TODO: add method_decl and constructor_decl

def p_field_decl(p):
	'''field_decl : modifier var_decl'''
	pass

def p_modifier(p):
	'''modifier : PUBLIC 
				| PUBLIC STATIC
				| PRIVATE
				| PRIVATE STATIC
				| STATIC
				| empty'''
	# TODO: Better to enumerate like this or to separate into distinct rules?
	pass

def p_var_decl(p):
	'''var_decl : type variables_nonempty SEMICOLON'''
	pass

def p_type(p):
	'''type : INT
			| FLOAT
			| BOOLEAN
			| ID'''
	pass

def p_variables_nonempty(p):
	'''variables_nonempty : variable variables'''
	pass

def p_variables(p):
	'''variables : COMMA variable variables
				 | empty'''
	pass 

def p_variable(p):
	'''variable : ID'''
	pass

def p_empty(p):
	'empty :'
	pass

def p_error(p):
	if p is not None:
		print("Syntax error on line {0} around token '{1}'".format(p.lineno, p.value))
	else:
		print("Unexpected end of file!")

	print("Exiting now.")
	exit(1)