decaflexer.py:
	Unchanged.
decafparser.py:
	Unchanged.
ast.py:
	Unchanged.
typecheck.py:
	Unchanged (except for some bug fixes).
codegen.py:
	The code for generating the machine code for the input program.
	First, it preprocesses the classes in the AST to create the necessary
	offsets (static and instance). Then it runs through each class and
	generates code for each method and constructor in turn, Each method
	body's code is generated recursively by calling `gen_code` on each
	statement and expression. The resulting code is incrementally added to
	the AbstractMachine (which is implicitly done in the constructor of the
	*Instruction classes).
absmc.py:
	Contains the classes used for generating the code including an
	AbstractMachine to store instructions, various Instruction classes to
	generate instructions, Registers and Labels. The instruction object are
	immediately added to the machine's instruction list upon creation,
	while labels must be manually added and will be applied to the next
	instruction.
decafc.py:
	A small driver script that reads in a file name, then performs the
	compilation on it. If any errors occur, they are printed out. Otherwise
	the generate machine code is printed out.
