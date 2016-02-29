from __future__ import print_function
from sys import exit
from decaflexer import tokens

def p_program(p):
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
    '''class_body_decl : field_decl
                       | method_decl
                       | constructor_decl'''
    pass

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
    # TODO: Get rid of this rule? Not really needed since we don't need
    # to support array access. Might be a cause of S/R conflicts in the
    # future. Feel free to replace this rule with just an ID if it solves
    # any S/R or R/R conflicts.
    pass

def p_method_decl(p):
    '''method_decl : modifier type ID LPAREN formals RPAREN block
                   | modifier VOID ID LPAREN formals RPAREN block'''
    # type and VOID can not be abstracted into a return_type rule!
    # This causes a S/R conflict where on seeing the ID,
    # it does not know whether to reduce the return_type or shift the ID
    # (for var_decl)
    pass

def p_constructor_decl(p):
    '''constructor_decl : modifier ID LPAREN formals RPAREN block'''

def p_formals(p):
    '''formals : formal_param formal_params
               | empty'''
    pass

def p_formal_param(p):
    '''formal_param : type variable'''
    pass

def p_formal_params(p):
    '''formal_params : COMMA formal_param formal_params
                     | empty'''
    pass

def p_block(p):
    '''block : LBRACE RBRACE'''
    # TODO: add statements and expressions
    pass

def p_empty(p):
    'empty :'
    pass

def p_error(p):
    if p is None:
        print("Unexcepted end of file!")
    else:
        last_newline = p.lexer.lexdata.rfind('\n', 0, p.lexpos)
        if last_newline < 0:
            last_newline = 0
        next_newline = p.lexer.lexdata.find('\n', p.lexpos)
        column = p.lexpos - last_newline
        
        print("Syntax error around '{0}' found on line {1}, column {2}:".format(
            p.value, p.lexer.lineno, column))
        print(p.lexer.lexdata[last_newline+1:next_newline])
    
    print("Exiting now.")
    exit(1)
