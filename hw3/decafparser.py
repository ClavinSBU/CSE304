import ply.yacc as yacc
import decaflexer
from decaflexer import tokens
from decaflexer import lex
import ast

import sys
import logging
precedence = (
    ('right', 'ASSIGN'),
    ('left', 'OR'),
    ('left', 'AND'),
    ('nonassoc', 'EQ', 'NEQ'),
    ('nonassoc', 'LEQ', 'GEQ', 'LT', 'GT'),
    ('left', 'PLUS', 'MINUS'),
    ('left', 'MULTIPLY', 'DIVIDE'),
    ('right', 'NOT'),
    ('right', 'UMINUS'),
    ('right', 'ELSE'),
    ('right', 'RPAREN'),
)


def init():
    ast.initAST()
    decaflexer.errorflag = False


### DECAF Grammar

# Top-level
def p_pgm(p):
    'pgm : class_decl_list'
    pass

def p_class_decl_list_nonempty(p):
    'class_decl_list : class_decl class_decl_list'
def p_class_decl_list_empty(p):
    'class_decl_list : '
    pass

def p_class_decl(p):
    'class_decl : class_name extends LBRACE class_body_decl_list RBRACE'
    ast.DecafClass(p[1], p[2])
def p_class_decl_error(p):
    'class_decl : class_name extends LBRACE error RBRACE'
    # error in class declaration; skip to next class decl.
    ast.DecafConstructor.flushContext(None)
    ast.DecafField.flushContext(None)
    ast.DecafMethod.flushContext(None)
def p_class_name(p):
    'class_name : CLASS ID'
    ast.DecafClass.current_class = p[2]
    p[0] = p[2]

def p_extends_id(p):
    'extends : EXTENDS ID '
    p[0] = p[2]
def p_extends_empty(p):
    ' extends : '
    p[0] = None

def p_class_body_decl_list_plus(p):
    'class_body_decl_list : class_body_decl_list class_body_decl'
    pass
def p_class_body_decl_list_single(p):
    'class_body_decl_list : class_body_decl'
    pass

def p_class_body_decl_field(p):
    'class_body_decl : field_decl'
    pass
def p_class_body_decl_method(p):
    'class_body_decl : method_decl'
    pass
def p_class_body_decl_constructor(p):
    'class_body_decl : constructor_decl'
    pass


# Field/Method/Constructor Declarations

def p_field_decl(p):
    'field_decl : mod var_decl'
    p[0] = p[1]  # Syntheize visibility and applicability
    for var in p[2]['vars']:
        ast.DecafField(var, p[0]['visibility'], p[0]['applicability'])
    # We weren't inside a method so let's ignore the context table and flush it
    ast.DecafVariable.flush_context()

def p_method_decl_void(p):
    'method_decl : mod VOID method_name LPAREN param_list_opt RPAREN block'
    ast.DecafMethod(p[3], p[1]['visibility'], p[1]['applicability'],
                    ast.DecafType.void(), p[7])
def p_method_decl_nonvoid(p):
    'method_decl : mod type method_name LPAREN param_list_opt RPAREN block'
    ast.DecafMethod(p[3], p[1]['visibility'], p[1]['applicability'], p[2],
                    p[7])
def p_method_name(p):
    'method_name : ID'
    ast.DecafMethod.current_method = p[1]
    p[0] = p[1]

def p_constructor_decl(p):
    'constructor_decl : mod constructor_name LPAREN param_list_opt RPAREN block'
    ast.DecafConstructor(p[1]['visibility'], p[6])
def p_constructor_name(p):
    'constructor_name : ID'
    ast.DecafConstructor.current_constructor = p[1]
    p[0] = p[1]


def p_mod(p):
    'mod : visibility_mod storage_mod'
    p[0] = {'visibility': p[1], 'applicability': p[2]}

def p_visibility_mod_pub(p):
    'visibility_mod : PUBLIC'
    p[0] = 'public'
def p_visibility_mod_priv(p):
    'visibility_mod : PRIVATE'
    p[0] = 'private'
def p_visibility_mod_empty(p):
    'visibility_mod : '
    p[0] = 'public'

def p_storage_mod_static(p):
    'storage_mod : STATIC'
    p[0] = 'class'
def p_storage_mod_empty(p):
    'storage_mod : '
    p[0] = 'instance'

def p_var_decl(p):
    'var_decl : type var_list SEMICOLON'
    p[0] = {'type': p[1], 'vars': p[2]['vars']}
    for var in p[0]['vars']:
        var.type = p[0]['type']


def p_type_int(p):
    'type :  INT'
    p[0] = ast.DecafType.int()
def p_type_bool(p):
    'type :  BOOLEAN'
    p[0] = ast.DecafType.boolean()
def p_type_float(p):
    'type :  FLOAT'
    p[0] = ast.DecafType.float()
def p_type_id(p):
    'type :  ID'
    p[0] = ast.DecafType.user_defined(p[1])

def p_var_list_plus(p):
    'var_list : var_list COMMA var'
    p[0] = {'vars': p[1]['vars']}
    p[0]['vars'].append(p[3])
def p_var_list_single(p):
    'var_list : var'
    p[0] = {'vars': [p[1]]}

def p_var_id(p):
    'var : ID'
    # We're unsure at this point if this is a field declaration or a variable
    # declaration inside a method. Let's assume the latter and just flush the
    # context table if it was actually a field declaration.
    p[0] = ast.DecafVariable.local(p[1])
def p_var_array(p):
    'var : var LBRACKET RBRACKET'
    pass

def p_param_list_opt(p):
    'param_list_opt : param_list'
    pass
def p_param_list_empty(p):
    'param_list_opt : '
    pass

def p_param_list(p):
    'param_list : param_list COMMA param'
    pass
def p_param_list_single(p):
    'param_list : param'
    pass

def p_param(p):
    'param : type ID'
    p[0] = ast.DecafVariable.formal(p[2], p[1])

# Statements

def p_block(p):
    'block : LBRACE block_begin stmt_list block_end RBRACE'
    p[0] = (p.linespan(0), 'Block', p[3])
def p_block_error(p):
    'block : LBRACE block_begin stmt_list error block_end RBRACE'
    # error within a block; skip to enclosing block
    p[0] = (p.linespan(0), 'Block', p[3])
def p_block_begin(p):
    'block_begin : '
    ast.DecafVariable.push_block()
    pass
def p_block_end(p):
    'block_end : '
    ast.DecafVariable.pop_block()
    pass

def p_stmt_list_empty(p):
    'stmt_list : '
    pass
def p_stmt_list(p):
    'stmt_list : stmt_list stmt'
    # We don't want to include var_decls in our method bodies
    if p[1] is None:
        p[0] = []
    else:
        p[0] = p[1]
    if p[2] is not None:
        p[0].append(p[2])

def p_stmt_if(p):
    '''stmt : IF LPAREN expr RPAREN stmt ELSE stmt
          | IF LPAREN expr RPAREN stmt'''
    if (len(p) > 6): # Case with 'if-else'
        p[0] = (p.linespan(0), 'If', p[3], 'Then', p[5], 'Else', p[7])
    else: # Case with just 'if'
        p[0] = (p.linespan(0), 'If', p[3], 'Then', p[5])

def p_stmt_while(p):
    'stmt : WHILE LPAREN expr RPAREN stmt'
    p[0] = (p.linespan(0), 'While', p[3], p[5])

def p_stmt_for(p):
    'stmt : FOR LPAREN stmt_expr_opt SEMICOLON expr_opt SEMICOLON stmt_expr_opt RPAREN stmt'
    p[0] = (p.linespan(0), 'For', p[3], p[5], p[7], p[9])

def p_stmt_return(p):
    'stmt : RETURN expr_opt SEMICOLON'
    p[0] = (p.linespan(0), 'Return', p[2])

def p_stmt_stmt_expr(p):
    'stmt : stmt_expr SEMICOLON'
    p[0] = p[1]
def p_stmt_break(p):
    'stmt : BREAK SEMICOLON'
    p[0] = 'Break'

def p_stmt_continue(p):
    'stmt : CONTINUE SEMICOLON'
    p[0] = 'Continue'

def p_stmt_block(p):
    'stmt : block'
    p[0] = p[1]

def p_stmt_var_decl(p):
    'stmt : var_decl'
    pass

def p_stmt_error(p):
    'stmt : error SEMICOLON'
    print("Invalid statement near line {}".format(p.lineno(1)))
    decaflexer.errorflag = True

# Expressions
def p_literal_int_const(p):
    'literal : INT_CONST'
    p[0] = (p.linespan(0), 'Integer-constant', p[1])
def p_literal_float_const(p):
    'literal : FLOAT_CONST'
    p[0] = (p.linespan(0), 'Float-constant', p[1])
def p_literal_string_const(p):
    'literal : STRING_CONST'
    p[0] = (p.linespan(0), 'String-constant', p[1])
def p_literal_null(p):
    'literal : NULL'
    p[0] = (p.linespan(0), 'Null-constant')
def p_literal_true(p):
    'literal : TRUE'
    p[0] = (p.linespan(0), 'True-constant')
def p_literal_false(p):
    'literal : FALSE'
    p[0] = (p.linespan(0), 'False-constant')

def p_primary_literal(p):
    'primary : literal'
    p[0] = (p.linespan(0), 'Constant', p[1])
def p_primary_this(p):
    'primary : THIS'
    p[0] = (p.linespan(0), 'This')
def p_primary_super(p):
    'primary : SUPER'
    p[0] = (p.linespan(0), 'Super')
def p_primary_paren(p):
    'primary : LPAREN expr RPAREN'
    p[0] = p[2]

def p_primary_newobj(p):
    'primary : NEW ID LPAREN start_args args_opt get_args_list RPAREN'
    p[0] = (p.linespan(0), 'New-object', p[2], p[6])

def p_primary_lhs(p):
    'primary : lhs'
    p[0] = p[1]
def p_primary_method_invocation(p):
    'primary : method_invocation'
    p[0] = p[1]

def p_args_opt_nonempty(p):
    'args_opt : arg_plus'
    pass
def p_args_opt_empty(p):
    'args_opt : '
    pass

def p_args_plus(p):
    'arg_plus : arg_plus COMMA expr'
    arg_list.append(p[3])

def p_args_single(p):
    'arg_plus : expr'
    arg_list.append(p[1])

def p_lhs(p):
    '''lhs : field_access
           | array_access'''
    p[0] = p[1]

def p_field_access_dot(p):
    'field_access : primary DOT ID'
    p[0] = (p.linespan(0), 'Field-access', p[1], p[3])
def p_field_access_id(p):
    'field_access : ID'
    # Check if this variable is in scope
    var = ast.DecafVariable.get_var_in_scope(p[1])
    if var is not None:
        # Variable found and in scope
        p[0] = (p.linespan(0), 'Variable', var.id)
        return
    # Otherwise, check if it's a reference to a class
    if p[1] == ast.DecafClass.current_class:
        p[0] = (p.linespan(0), 'Class', p[1])
        return
    for decaf_class in ast.DecafClass.table:
        if p[1] == decaf_class.name:
            p[0] = (p.linespan(0), 'Class', p[1])
            return
    # At this point, we have an error
    print("Unknown class or variable {} at line {}".format(p[1], p.lineno(1)))
    raise SyntaxError

def p_array_access(p):
    'array_access : primary LBRACKET expr RBRACKET'
    pass


arg_list = []
def p_method_invocation(p):
    'method_invocation : field_access LPAREN start_args args_opt get_args_list RPAREN'
    p[0] = (p.linespan(0), 'Method-call', p[1], p[5])

def p_start_method_call(p):
    'start_args : '
    del arg_list[:]

def p_get_args_list(p):
    'get_args_list : '
    p[0] = arg_list

def p_expr_basic(p):
    '''expr : primary
            | assign
            | new_array'''
    p[0] = p[1]
def p_expr_binop(p):
    '''expr : expr PLUS expr
            | expr MINUS expr
            | expr MULTIPLY expr
            | expr DIVIDE expr
            | expr EQ expr
            | expr NEQ expr
            | expr LT expr
            | expr LEQ expr
            | expr GT expr
            | expr GEQ expr
            | expr AND expr
            | expr OR expr
    '''

    if p[2] == '+': operator = 'add'
    elif p[2] == '-': operator = 'sub'
    elif p[2] == '*': operator = 'mult'
    elif p[2] == '/': operator = 'div'
    elif p[2] == '==': operator = 'equal'
    elif p[2] == '!=': operator = 'not-equal'
    elif p[2] == '<': operator = 'less-than'
    elif p[2] == '<=': operator = 'less-than-or-equal'
    elif p[2] == '>': operator = 'greater-than'
    elif p[2] == '>=': operator = 'greater-than-or-equal'
    elif p[2] == '&&': operator = 'and'
    else: operator = 'or'

    p[0] = (p.linespan(0), 'Binary', operator, p[1], p[3])

def p_expr_unop(p):
    '''expr : PLUS expr %prec UMINUS
            | MINUS expr %prec UMINUS
            | NOT expr'''

    if p[1] == '+': operator = 'positive'
    elif p[1] == '-': operator = 'negative'
    else: operator = 'not'

    p[0] = (p.linespan(0), 'Unary', p[2], operator)

def p_assign_equals(p):
    'assign : lhs ASSIGN expr'
    p[0] = (p.linespan(0), 'Assign', p[1], p[3])
def p_assign_post_inc(p):
    'assign : lhs INC'
    p[0] = (p.linespan(0), 'Auto', p[1], 'inc', 'post')

def p_assign_pre_inc(p):
    'assign : INC lhs'
    p[0] = (p.linespan(0), 'Auto', p[1], 'inc', 'pre')

def p_assign_post_dec(p):
    'assign : lhs DEC'
    p[0] = (p.linespan(0), 'Auto', p[1], 'dec', 'post')

def p_assign_pre_dec(p):
    'assign : DEC lhs'
    p[0] = (p.linespan(0), 'Auto', p[1], 'dec', 'pre')

def p_new_array(p):
    'new_array : NEW type dim_expr_plus dim_star'
    pass

def p_dim_expr_plus(p):
    'dim_expr_plus : dim_expr_plus dim_expr'
    pass
def p_dim_expr_single(p):
    'dim_expr_plus : dim_expr'
    pass

def p_dim_expr(p):
    'dim_expr : LBRACKET expr RBRACKET'
    pass

def p_dim_star(p):
    'dim_star : LBRACKET RBRACKET dim_star'
    pass
def p_dim_star_empty(p):
    'dim_star : '
    pass

def p_stmt_expr(p):
    '''stmt_expr : assign
                 | method_invocation'''
    p[0] = (p.linespan(0), 'Expr', p[1])

def p_stmt_expr_opt(p):
    'stmt_expr_opt : stmt_expr'
    p[0] = p[1]

def p_stmt_expr_empty(p):
    'stmt_expr_opt : '
    pass

def p_expr_opt(p):
    'expr_opt : expr'
    p[0] = (p.linespan(0), 'Expr', p[1])

def p_expr_empty(p):
    'expr_opt : '
    pass


def p_error(p):
    if p is None:
        print ("Unexpected end-of-file")
    else:
        print ("Unexpected token '{0}' near line {1}".format(p.value, p.lineno))
    decaflexer.errorflag = True

parser = yacc.yacc()

def from_file(filename):
    try:
        with open(filename, "rU") as f:
            init()
            parser.parse(f.read(), lexer=lex.lex(module=decaflexer),
                         debug=None, tracking=True)
        return not decaflexer.errorflag
    except IOError as e:
        print "I/O error: %s: %s" % (filename, e.strerror)


if __name__ == "__main__" :
    f = open(sys.argv[1], "r")
    logging.basicConfig(
            level=logging.CRITICAL,
    )
    log = logging.getLogger()
    res = parser.parse(f.read(), lexer=lex.lex(module=decaflexer), debug=log)

    if parser.errorok :
        print("Parse succeed")
    else:
        print("Parse failed")
