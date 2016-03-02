from __future__ import print_function
from sys import exit
from decaflexer import tokens

precedence = (
    ('right', 'EQUALS'),
    ('left', 'OR'),
    ('left', 'AND'),
    ('left', 'EQ', 'NE'),
    ('nonassoc', 'LT', 'GT', 'LTE', 'GTE'),
    ('left', 'PLUS', 'MINUS'),
    ('left', 'MULT', 'DIV'),
    ('right', 'UMINUS', 'UPLUS', 'NOT')
)

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
    '''block : LBRACE stmts RBRACE'''
    # TODO: add statements and expressions
    pass

def p_stmt(p):
    '''stmt : IF LPAREN expr RPAREN stmt
            | IF LPAREN expr RPAREN stmt ELSE stmt
            | WHILE LPAREN expr RPAREN stmt
            | FOR LPAREN stmt_expr_empty SEMICOLON expr_empty SEMICOLON stmt_expr_empty RPAREN stmt
            | RETURN expr_empty SEMICOLON
            | stmt_expr SEMICOLON
            | BREAK SEMICOLON
            | CONTINUE SEMICOLON
            | block
            | var_decl
            | SEMICOLON'''
    pass

def p_stmts(p):
    '''stmts : stmt stmts
             | empty'''
    pass

def p_literal(p):
    '''literal : INTCONST
               | FLOATCONST
               | STRINGCONST
               | NULL
               | TRUE
               | FALSE'''
    pass

def p_primary(p):
    '''primary : literal
               | THIS
               | SUPER
               | LPAREN expr RPAREN
               | NEW ID LPAREN arguments RPAREN
               | NEW ID LPAREN RPAREN
               | lhs
               | method_invocation'''
    pass

def p_arguments(p):
    '''arguments : expr arguments_s'''
    pass

def p_arguments_s(p):
    '''arguments_s : COMMA expr arguments_s
                   | empty'''
    #TODO: rename this function, or set convention for these types of helper functions
    pass

def p_lhs(p):
    '''lhs : field_access'''
    #TODO: add array_access when we get to the point where 304 has to do arrays
    pass

def p_field_access(p):
    '''field_access : primary DOT ID
                    | ID'''
    pass

#TODO: add array_access definition

def p_method_invocation(p):
    '''method_invocation : field_access LPAREN arguments RPAREN
                         | field_access LPAREN RPAREN'''
    pass

def p_expr(p):
    '''expr : primary
            | assign
            | expr PLUS expr
            | expr MINUS expr
            | expr MULT expr
            | expr DIV expr
            | expr AND expr
            | expr OR expr
            | expr EQ expr
            | expr NE expr
            | expr LT expr
            | expr GT expr
            | expr LTE expr
            | expr GTE expr
            | PLUS expr %prec UPLUS
            | MINUS expr %prec UMINUS
            | NOT expr'''
    #TODO: add new_array
    pass

def p_expr_empty(p):
    '''expr_empty : expr
                  | empty'''
    pass

def p_assign(p):
    '''assign : lhs EQUALS expr
              | lhs INC
              | INC lhs
              | lhs DEC
              | DEC lhs'''
    pass
    #TODO: add new_array definition

def p_stmt_expr(p):
    '''stmt_expr : assign
                 | method_invocation'''
    pass

def p_stmt_expr_empty(p):
    '''stmt_expr_empty : stmt_expr
                       | empty'''

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
