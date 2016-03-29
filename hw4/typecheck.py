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
        # Calculate the type of the condition
        expr_error(stmt.condition)
        if stmt.condition.type != ast.Type('boolean'):
            signal_error('Was expecting a boolean condition. Got a condition'
                         ' of {0} instead.'.format(stmt.condition.type),
                         stmt.lines)
            stmt.error = True
        if stmt_error(stmt.thenpart) or stmt_error(stmt.elsepart):
            stmt.error = True

    elif isinstance(stmt, ast.WhileStmt):
        if stmt.condition.type != ast.Type('boolean'):
            signal_error('Was expecting a boolean condition. Got a condition'
                         ' of {0} instead.'.format(stmt.condition.type),
                         stmt.lines)
            stmt.error = True
        if stmt_error(stmt.body):
            stmt.error = True

    elif isinstance(stmt, ast.ForStmt):
        if stmt.condition.type != ast.Type('boolean'):
            signal_error('Was expecting a boolean condition.', stmt.lines)
            stmt.error = True
        if (stmt_error(stmt.init) or expr_error(stmt.cond) or
            stmt_error(stmt.update) or stmt_error(stmt.body)):
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
            # Must call expr_error before we can check stmt.expr.type
            # because type is not calculated until expr_error is called.
            if expr_error(stmt.expr):
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
    expr.type = ast.Type('null')  # TODO: actually calculate the type
    return False


def signal_error(string, lineno):
    global error_flag
    print "{1}: {0}".format(string, lineno)
    error_flag = True
