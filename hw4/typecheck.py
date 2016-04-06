import ast

error_flag = False
current_class = None
current_method = None


def check_classes(classtable):
    for cls in classtable.viewvalues():
        check_class(cls)


def check_class(cls):
    global current_class, current_method
    current_class = cls

    for method in cls.methods:
        current_method = method
        stmt_error(method.body)
    for constr in cls.constructors:
        current_method = method
        stmt_error(method.body)
    current_method = None


def stmt_error(stmt):
    '''Return whether or not the statement has a type or resolution error.'''
    stmt.error = False

    if isinstance(stmt, ast.BlockStmt):
        block_error = False
        for stmt_line in stmt.stmtlist:
            if stmt_error(stmt_line):
                block_error = True
        stmt.error = block_error

    elif isinstance(stmt, ast.IfStmt):
        cond_err = expr_error(stmt.condition)
        then_err = stmt_error(stmt.thenpart)
        else_err = stmt_error(stmt.elsepart)
        bool_type = ast.Type('boolean')
        if cond_err:
            stmt.error = True
        elif not stmt.condition.type == bool_type:
            signal_error('Expecting a boolean condition. Got a condition'
                         ' of {0} instead.'.format(stmt.condition.type),
                         stmt.lines)
            stmt.error = True
        elif then_err or else_err:
            stmt.error = True

    elif isinstance(stmt, ast.WhileStmt):
        cond_err = expr_error(stmt.cond)
        body_err = stmt_error(stmt.body)
        if cond_error:
            stmt.error = True
        elif stmt.condition.type != ast.Type('boolean'):
            signal_error('Expecting a boolean condition. Got a condition'
                         ' of {0} instead.'.format(stmt.cond.type),
                         stmt.lines)
            stmt.error = True
        elif body_err:
            stmt.error = True

    elif isinstance(stmt, ast.ForStmt):
        init_err = stmt_error(stmt.init)
        cond_err = expr_error(stmt.cond)
        update_err = stmt_error(stmt.update)
        body_err = stmt_error(stmt.body)
        if cond_error:
            stmt.error = True
        elif stmt.cond.type != ast.Type('boolean'):
            signal_error('Expecting a boolean condition. Got a condition'
                         ' of {0} instead.'.format(stmt.cond.type),
                         stmt.lines)
            stmt.error = True
        elif init_err or update_err or body_err:
            stmt.error = True

    elif isinstance(stmt, ast.ReturnStmt):
        global current_method
        rtype = current_method.rtype
        if stmt.expr is None:
            if rtype != ast.Type('void'):
                signal_error(
                    'Method {0} in class {1} has non-void return type but '
                    'return statement has no expression.'.format(
                        current_method.name, current_class.name),
                    stmt.lines)
                stmt.error = True
        else:
            expr_err = expr_error(stmt.expr)
            if expr_err:
                stmt.error = True
            elif not stmt.expr.type.subtype_of(rtype):
                signal_error(
                    'Method {0} in class {1} expecting a return type of {2} '
                    'but return statement has a type of {3}. This is not a '
                    'subtype of {2}.'.format(
                        current_method.name, current_class.name, rtype,
                        stmt.expr.type),
                    stmt.lines)
                stmt.error = True
            else:
                stmt.error = False

    elif isinstance(stmt, ast.ExprStmt):
        stmt.error = expr_error(stmt.expr)

    elif (isinstance(stmt, ast.BreakStmt) or
          isinstance(stmt, ast.ContinueStmt) or
          isinstance(stmt, ast.SkipStmt)):
        # Trivially, these statements are type correct
        stmt.error = False

    return stmt.error


def expr_error(expr):
    '''Return whether or not the expression has a type or resolution error.

    Also ensures that the type of the expression is calculated. Call this
    first if you need to use the type of an expression.'''
    expr.type = None

    if isinstance(expr, ast.ConstantExpr):
        if expr.kind == 'int' or expr.kind == 'float' or expr.kind == 'string':
            expr.type = ast.Type(expr.kind)
        elif expr.kind == 'Null':
            expr.type = ast.Type('null')
        elif expr.kind == 'True' or expr.kind == 'False':
            expr.type = ast.Type('boolean')
        else:
            expr.type = ast.Type('error')
            signal_error('Unknown type {}'.format(expr.type), expr.lines)

    elif isinstance(expr, ast.VarExpr):
        expr.type = expr.var.type

    elif isinstance(expr, ast.UnaryExpr):
        arg = expr.arg
        arg_err = expr_error(arg)
        if arg_err:
            expr.type = ast.Type('error')
        elif expr.uop == 'uminus':
            if arg.type.is_numeric():
                expr.type = arg.type
            else:
                signal_error('Expecting an integer or float argument to unary '
                             'minus. Found {}'.format(arg.type), expr.lines)
                expr.type = ast.Type('error')
        elif expr.uop == 'neg':
            if arg.type == ast.Type('boolean'):
                expr.type = arg.type
            else:
                signal_error('Expecting a boolean argument to ! (negation). '
                             'Found {}'.format(arg.type), expr.lines)
                expr.type = ast.Type('error')

    elif isinstance(expr, ast.BinaryExpr):
        op_names = {'add': '+', 'sub': '-', 'mul': '*', 'div': '/',
                           'and': '&&', 'or': '||', 'eq': '==', 'neq': '!=',
                           'lt': '<', 'leq': '<=', 'gt': '>', 'geq': '>='}
        bop = expr.bop
        arg1 = expr.arg1
        arg2 = expr.arg2
        arg1_err = expr_error(arg1)
        arg2_err = expr_error(arg2)
        if arg1_err or arg2_err:
            expr.type = ast.Type('error')
        elif bop == 'add' or bop == 'sub' or bop == 'mul' or bop == 'div':
            type1 = arg1.type
            type2 = arg2.type
            if type1.is_numeric() and type2.is_numeric():
                if type1 == ast.Type('float') or type2 == ast.Type('float'):
                    expr.type = ast.Type('float')
                else:
                    expr.type = ast.Type('int')
            else:
                signal_error('Expecting float or integer arguments for the '
                             'operator "{}". Found {} on the left and {} on '
                             'the right.'.format(op_names[bop], type1, type2),
                             expr.lines)
                expr.type = ast.Type('error')
        elif bop == 'and' or bop == 'or':
            # TODO: Check the specification. I believe there is an error in it.
            # The homework says the "Boolean operations and, or: have type int
            # if both operands have type boolean..." This should be type
            # boolean, if I understand it correctly.
            type1 = arg1.type
            type2 = arg2.type
            if type1 == ast.Type('boolean') and type2 == ast.Type('boolean'):
                expr.type = ast.Type('boolean')
            else:
                signal_error('Expecting boolean arguments for the operator '
                             '"{}". Found {} on the left and {} on the '
                             'right.'.format(op_names[bop], type1, type2),
                             expr.lines)
        elif bop == 'lt' or bop == 'leq' or bop == 'gt' or bop == 'geq':
            type1 = arg1.type
            type2 = arg2.type
            if type1.is_numeric() and type2.is_numeric():
                expr.type = ast.Type('boolean')
            else:
                signal_error('Expecting int or float arguments for the'
                             'operator "{}". Found {} on the left and {} on '
                             'the right.'.format(op_names[bop], type1, type2),
                             expr.lines)
                expr.type = ast.Type('error')
        elif bop == 'eq' or bop == 'neq':
            type1 = arg1.type
            type2 = arg2.type
            if type1.subtype_of(type2) or type2.subtype_of(type1):
                expr.type = ast.Type('boolean')
            else:
                signal_error('Expecting compatible arguments for the operator '
                             '"{}". One argument must be the subtype of the '
                             'other. Found {} on the left and {} on the '
                             'right.'.format(op_names[bop], type1, type2),
                             expr.lines)
                expr.type = ast.Type('error')

    elif isinstance(expr, ast.FieldAccessExpr):

        err = expr_error(expr.base)
        if err:
            print 'error' + str(expr.lines)
            expr.type = ast.Type('null')

        cls = ast.lookup(ast.classtable, expr.base.type.typename)

        field = ast.lookup(cls.fields, expr.fname)

        expr.type = ast.Type(field.type)

    elif isinstance(expr, ast.ThisExpr):
        expr.type = ast.Type(current_class.name)

    elif isinstance(expr, ast.MethodInvocationExpr):

        err = expr_error(expr.base)

        cls = ast.lookup(ast.classtable, expr.base.type.typename)

        method = None

        for i in cls.methods:
            if expr.mname == i.name:
                method = i
                break

        expr.type = ast.Type(method.rtype)

    elif isinstance(expr, ast.AssignExpr):

        lhs_err = expr_error(expr.lhs)
        rhs_err = expr_error(expr.rhs)

        if lhs_err or rhs_err:
            print 'Not type checked'
            expr.type = ast.Type('error')

        lhs = ast.Type(expr.lhs.type)
        rhs = ast.Type(expr.rhs.type)

        if not rhs.subtype_of(lhs):
            print 'Not a subtype'
            expr.type = ast.Type('error')
            signal_error('', expr.lines)
        else:
            expr.type = ast.Type(rhs)

    elif isinstance(expr, ast.NewObjectExpr):
        expr.type = ast.Type(expr.classref.name)

    else:
        # Placeholder for not-implemented expressions
        # TODO: Remove this case when done
        print 'IMPLEMENT'
        print type(expr)
        expr.type = ast.Type('null')

    return expr.type.is_error()


def signal_error(string, lineno):
    global error_flag
    print "{1}: {0}".format(string, lineno)
    error_flag = True
