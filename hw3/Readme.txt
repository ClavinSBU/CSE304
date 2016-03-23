decaflexer.py:
    This is unchanged from the professor's HW2 implementation.

decafparser.py:
    This contains the ply/yacc code, modified from the professor's reference
    implementation. The parser rules remain mainly unchanged, except in the case
    of class_decl, method_decl, constructor_decl, where was rule was added so
    that we could get the current class/method/constructor name before it is
    fully parsed. Two embedded actions were also added to the block rule for the
    purpose of tracking variable scopes.

    Most of the information passed through the parse tree is kept in tuple-form
    until the unit is fully parsed, in which case we construct a new object from
    ast.py. The exception is variables. Upon seeing the variable id, a non-typed
    variable object will be created. The type will be added on after it is seen.

    For simplicity, expressions and statements are always represented as tuples,
    with no class representation. The first element of the tuple is always the
    linespan (returned from p.linespan()). The second element denotes the kind
    of statement or expression ('For', 'While', 'Binary', etc.). The rest of the
    elements, if there are any, contain any other information that is needed.

    Uniqueness constraints are generally performed after a complete parse of the
    entity. Class name uniqueness is checked after the class is fully parsed.
    Fields are checked after a complete field declaration. Parameters are
    checked when the full parameter list has been seen. Variables are checked
    after the full variable declaration has been seen.
    
ast.py:
    This contains the objects to represent different structural units within the
    program, including Classes, Methods, Constructors, Fields, Types, and
    Variables.

    Some classes (DecafConstructor, DecafMethod, DecafField, and DecafVariable)
    make use of a 'context.' The 'context' is a per-class static table that is
    incrementally added to until it is flushed. Flushing happens when a
    significant point is reached, like the end of a method, constructor, field,
    or class declaration. Specifically, the DecafVariable.context table is
    populated during a field declaration or a function body and is flushed at
    the end of either of those. The other context tables are flushed at the end
    of a class. Flushing will either throw away the accumulated objects or store
    them in another table. Variables are flushed into the corresponding method
    variable table, while all other objects are flushed into global tables.

    DecafClass.table, DecafMethod.table, DecafConstructor.table, and
    DecafField.table serve to globally store the entities after they are
    flushed.

    The AST printing and initialization code is also here. Inititalization (of
    In and Out) occurs in initAST. Printing of the objects is performed within
    each class's __str__ method. Printing of statements and expressions is
    performed within stmt_to_string.

    The final mention of note is DecafVariable.scope. It is a two-dimensional
    array of variables. The formal parameters reside within the first inner
    array. The top-most block's local variables are in the second inner array.
    These two array exist throughout the parsing of a function body. Any other
    arrays are dynamically pushed and popped as blocks come in and out of scope.
    One caveat of this approach is that formal parameters are treated as a
    separate scope from top-most local variables, so this has to be
    special-cased (in decafparser.py) to adhere to the uniqueness specification.

decafch.py:
    This is largely unchanged from the professor's HW2 implementation. The only
    difference is that a print_ast function was added to print the class table.
    This is called only after a successful parse.
