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
        if cond_err:
            stmt.error = True
        elif stmt.cond.type != ast.Type('boolean'):
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
        if cond_err:
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
            expr.type = ast.Type('error')
            return True

        cls = ast.lookup(ast.classtable, expr.base.type.typename)

        cur_cls = cls
        while cur_cls is not None:
            field = ast.lookup(cur_cls.fields, expr.fname)
            if field is not None:

                # Ensure it's not static, and not accessed by Class.foo, and it's accessable
                if (expr.base.type.kind == 'class') and (field.storage != 'static') \
                        and ((field.visibility != 'private') or (expr.base.type.typename == current_class.name)):
                    break

                # Ensure it's static, and accessed by Class.foo, and it's accessable
                if (expr.base.type.kind == 'class-literal') and (field.storage == 'static') \
                        and ((field.visibility != 'private') or (expr.base.type.typename == current_class.name)):
                    break
            field = None
            cur_cls = cur_cls.superclass

        if field is None:
            signal_error('Could not resolve field {}'.format(expr.fname), expr.lines)
            expr.type = ast.Type('error')
            return True

        expr.type = ast.Type(field.type)

    elif isinstance(expr, ast.ThisExpr):
        expr.type = ast.Type(current_class.name)

    elif isinstance(expr, ast.MethodInvocationExpr):

        err = expr_error(expr.base)
        if err:
            expr.type = ast.Type('error')
            return True

        cls = ast.lookup(ast.classtable, expr.base.type.typename)
        method = None
        cur_cls = cls

        while cur_cls is not None:
            for i in cur_cls.methods:
                if expr.mname == i.name:
                    method = i
                    break

            if method is not None:
                if (expr.base.type.kind == 'class') and (method.storage != 'static') \
                        and ((method.visibility != 'private') or (expr.base.type.typename == current_class.name)):
                    break

                if (expr.base.type.kind == 'class-literal') and (method.storage == 'static') \
                        and ((method.visibility != 'private') or (expr.base.type.typename == current_class.name)):
                    break
            method = None
            cur_cls = cur_cls.superclass

        if method is None:
            expr.type = ast.Type('error')
            signal_error('Could not resolve method \'{}\''.format(expr.mname), expr.lines)
            return True

        method_params = method.vars.vars[0].values()

        # Ensure number of params match
        if len(method_params) != len(expr.args):
            expr.type = ast.Type('error')
            signal_error('Method \'{}\' expects {} args, received {}'.format(
                method.name, len(method_params), len(expr.args)), expr.lines)
            return True

        for i in range(0, len(method_params)):

            arg_err = expr_error(expr.args[i])
            if arg_err:
                expr.type = ast.Type('error')
                return True

            nth_param = ast.Type(method_params[i].type)
            nth_arg = ast.Type(expr.args[i].type)

            if not nth_arg.subtype_of(nth_param):
                expr.type = ast.Type('error')
                signal_error(
                    'Method argument number {0} is not a subtype '
                    'of construtor parameter number {0}. Expects \'{1}\', received \'{2}\'.'.format(
                        i + 1, nth_param.typename, nth_arg.typename), expr.lines)
                return True

        expr.type = ast.Type(method.rtype)

    elif isinstance(expr, ast.AssignExpr):

        lhs_err = expr_error(expr.lhs)
        rhs_err = expr_error(expr.rhs)

        if lhs_err or rhs_err:
            expr.type = ast.Type('error')
            return True

        lhs = ast.Type(expr.lhs.type)
        rhs = ast.Type(expr.rhs.type)

        if not rhs.subtype_of(lhs):
            expr.type = ast.Type('error')
            signal_error('{} not a subtype of {}'.format(rhs, lhs), expr.lines)
        else:
            expr.type = ast.Type(rhs)

    elif isinstance(expr, ast.NewObjectExpr):

        cls = ast.lookup(ast.classtable, expr.classref.name)

        # After ensuring the # of args match, if there's no constructor, allow it
        if len(cls.constructors) == 0 and len(expr.args) == 0:
            expr.type = ast.Type(expr.classref.name)
            return False

        if cls.constructors[0].visibility == 'private':
            expr.type = ast.Type('error')
            signal_error('Constructor for class {} is private'.format(
                cls.name), expr.lines)
            return True

        # Ensure number of args match
        if len(cls.constructors[0].vars.vars[0]) != len(expr.args):
            expr.type = ast.Type('error')
            signal_error('Constructor for class {} expects {} arguments, received {}'.format(
                cls.name, len(cls.constructors[0].vars.vars[0]), len(expr.args)), expr.lines)
            return True

        constr_params = cls.constructors[0].vars.vars[0].values()
        # Ensure each arg is a subtype of each param
        for i in range(0, len(constr_params)):

            arg_err = expr_error(expr.args[i])
            if arg_err:
                expr.type = ast.Type('error')
                return True

            nth_param = ast.Type(constr_params[i].type)
            nth_arg = ast.Type(expr.args[i].type)

            if not nth_arg.subtype_of(nth_param):
                expr.type = ast.Type('error')
                signal_error(
                    'Constructor argument number {0} is not a subtype '
                    'of construtor parameter number {0}. Expects \'{1}\', received \'{2}\'.'.format(
                        i + 1, nth_param.typename, nth_arg.typename), expr.lines)
                return True

        expr.constr_id = cls.constructors[0].id
        expr.type = ast.Type(expr.classref.name)

    elif isinstance(expr, ast.ClassReferenceExpr):
        expr.type = ast.Type(expr.classref.name, None, True)

    elif isinstance(expr, ast.SuperExpr):
        if current_class.superclass is None:
            signal_error('Class {} has no superclass.'.format(current_class.name), expr.lines)
            expr.type = ast.Type('error')
        else:
            expr.type = ast.Type(current_class.superclass.name)

    elif isinstance(expr, ast.AutoExpr):

        err = expr_error(expr.arg)
        if err:
            expr.type = ast.Type('error')
            return True

        if expr.arg.type.is_numeric():
            expr.type = ast.Type(expr.arg.type)
        else:
            expr.type = ast.Type('error')
            signal_error('Auto expression must be int or float; received {}'.format(expr.arg.type), expr.lines)

    return expr.type.is_error()


def signal_error(string, lineno):
    global error_flag
    print "{1}: {0}".format(string, lineno)
    error_flag = True
