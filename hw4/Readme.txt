decaflexer.py:
    This is unchanged from the professor's HW2 implementation.

decafparser.py:
    This is unchanged from the professor's HW3 implementation.
    
ast.py:
    This is unchanged from the professor's HW3 implementation.

typecheck.py
    This is our typechecker. We run through each statement and expression made
    in our AST and ensure that our compiler does not output programs with
    undefined behavior that can be caught in the compilation stage.


decafch.py:
    This is largely unchanged from the professor's HW3 implementation. The only
    difference is that we now type check all statements and expressions. If
    there are no errors, we print the AST. If there are errors, we print the
    line number as well as the error.
