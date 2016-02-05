from __future__ import print_function # gives us Python 3's print backported 
import sys, re

# TODO:
# Should we allow integers with a leading zero?
# What about leading pluses ('+')?
# Relevant line in the HW:
#     An integer num is a sequence of numeric characters, optionally preceded by a minus ("-")
#
# Test if double (or triple, etc.) labels are supported
#
# Remove 'Final value is:' before hand-in
#
# Remove TEST opcode before hand-in
#
# Possibly replace Parser._is_valid_label with a regex implementation??

class Stack(object):
    """Basic implementation of a stack data structure.

    This implementation supports the standard push, pop, and peek operations.
    """

    def __init__(self):
        self._items = []

    def push(self, value):
        """Pushes value on top of the stack

        Args:
            value: The integer value to push onto the stack.
        """
        print_debug("Pushing {0}".format(value))
        # The following cast is necessary because value can either be 
        # 1) an int from an arithmetic operation, etc.
        # 2) a string from an ildc
        self._items.append(int(value))

    def pop(self):
        """Pops the top-most value off the stack.

        If the stack is empty, emits an error message and exits with code 1.

        Returns:
            The integer value popped off the stack.
        """
        print_debug("Was {0}".format(self._items))
        if len(self._items) == 0:
            print_error("Stack is empty, exiting")

        ret = self._items.pop()
        print_debug("Popping {0}".format(ret))
        print_debug("Now {0}".format(self._items))
        return ret

    def peek(self):
        """Peeks into the stack.

        If the stack is empty, emits an error message and exits with code 1.

        Returns:
            The integer value on top of the stack.
        """
        if len(self._items) == 0:
            print_error("Stack is empty, exiting")
        return self._items[-1]

    def __str__(self):
        """A string representation of the stack.

        The first element is "on the bottom", the last "on the top."
        """
        return str(self._items);

class Program(object):
    """Structured representation of the source code used for execution

    Well-formed instruction (see the Instruction class) are incrementally added
    to the program with the addInstruction method. Labels are added into a
    dictionary with addLabel. The program will be run when execute is called.
    Upon completion of execution, the top-most value on the stack will be printed.
    """

    def __init__(self):
        self._labels = {}
        self._instructions = []
        self._store = {} # the directly-addressed memory area
        self._stack = Stack()

    @property
    def labels(self):
        """labels (Dict<String, int>): a mapping of labels to instruction numbers"""
        return self._labels
    
    @property
    def instructions(self):
        """instructions (List[Instruction]): the list of well-formed instructions

        The program will run through these sequentially on execution.
        """
        return self._instructions
    

    def execute(self):
        """Executes the instructions starting from the first.

        This will terminate when the program counter reaches past the
        instruction array (i.e. when the last instruction has been executed).

        Returns:
            On termination, it will return the top-most value off the stack.
        """
        pc = 0 # pc is 0, run the first (0th) instruction
        while pc < len(self._instructions):
            op = self._instructions[pc].opcode
            arg = self._instructions[pc].arg # May be None
            print_debug('{0}: {1}'.format(pc, self._instructions[pc]))

            if op == 'ildc':
                self._stack.push(arg)

            elif op == 'iadd':
                # The add, sub, etc functions all pop the first two elements
                # and do the desired operation on it, so since they all are
                # the same except for the actual operation, use one function
                # and use logic to find out which operation.
                self._imath('+')

            elif op == 'isub':
                self._imath('-')

            elif op == 'imul':
                self._imath( '*')

            elif op == 'idiv':
                self._imath('/')

            elif op == 'imod':
                self._imath('%')

            elif op == 'pop':
                self._stack.pop()

            elif op == 'dup':
                self._stack.push(self._stack.peek())

            elif op == 'swap':
                first = self._stack.pop()
                second = self._stack.pop()
                self._stack.push(first)
                self._stack.push(second)

            elif op == 'jz':
                top = self._stack.pop()
                if top == 0:
                    pc = self._labels.get(arg)
                    if pc is None:
                        print_error("Illegal jump performed to undefined label '{}'".format(instruction))
                    continue

            elif op == 'jnz':
                top = self._stack.pop()
                if top != 0:
                    pc = self._labels.get(arg)
                    if pc is None:
                        print_error("Illegal jump performed to undefined label '{}'".format(instruction))
                    continue

            elif op == 'jmp':
                pc = self._labels.get(arg)
                if pc is None:
                    print_error("Illegal jump performed to undefined label '{}'".format(instruction))
                continue

            elif op == 'load':
                address = self._stack.pop()
                print_debug(address)

                value = self._store.get(address)
                if value is None:
                    print_error("Store address '{0}' not initialized, exiting.".format(address))

                print_debug(value)
                self._stack.push(value)

            elif op == 'store':
                value = self._stack.pop()
                address = self._stack.pop()
                self._store[address] = value
                print_debug(self._store)

            elif op == 'TEST':
                print_debug(self._stack)

            else:
                print_error("Instruction not found '{0}'".format(op))

            print_debug(self._stack)
            pc += 1 # Advance to next instruction after current one is completed.
                    # After pc is set with a jump instruction, it is 'continue'd
                    # so we never make it here if the instruction is a jump

        return self._stack.peek()

    def addInstruction(self, instruction):
        """Adds an instruction to the end of the instructions list.

        Args:
            instruction: The Instruction object to append to the instructions.
        """
        self._instructions.append(instruction)

    def addLabel(self, label, instruction_number):
        """Adds a label and its associated instruction number to the label map.

        Args:
            label: The string label to be referenced by a jump-type instruction.
            instruction_number: An integer value i would map the given label to
                the ith instruction.
        """
        self._labels[label] = instruction_number

    def _imath(self, operation):
        """Performs binary arithmetic operations on the top of the stack.

        In summary, this will pop off two values from the stack. It will then
        compute the second value OPERATION the first value, where OPERATION is
        a binary arithmetic operation. It will then push the result onto the
        stack.

        The supported binary math operations are: +, -, *, /, and %. If an
        unsupported operation is passed in, this will emit an error message
        and exit.

        Args:
            operation: a character representing the operation to perform
        """
        first = self._stack.pop()
        second = self._stack.pop()

        if operation == '+':
            self._stack.push(second + first)

        elif operation == '-':
            self._stack.push(second - first)

        elif operation == '*':
            self._stack.push(second * first)

        elif operation == '/':
            self._stack.push(second / first)

        elif operation == '%':
            self._stack.push(second % first)

        else:
            print_error("Unknown math operation '{0}'".format(operand))

    def __str__(self):
        """Returns the list of instructions and the label mapping.

        The instructions are printed with prepended 1-indexed line numbers.

        The labels are printed separately in the format LABEL: LINE_NUM where
        LABEL is the label name and LINE_NUM is the 1-indexed line it refers to.
        """
        # Probably some performance issues with this code because of Python's
        # immutable strings. This code is only ever called in development or
        # testing, so it should be fine.
        i = 1
        result_string = ""
        for line in self._instructions:
            result_string += "{0}: {1}\n".format(i, line)
            i += 1

        result_string += 'Labels:'
        for label, line_number in self._labels.iteritems():
            result_string += "\n\t{0}: {1}".format(label, line_number+1)
            # Added 1 because the line numbers are stored 0-indexed,
            # but we are printing 1-indexed line numbers.

        return result_string

class Instruction(object):
    """Structured representation of a well-formatted Instruction"""

    def __init__(self, opcode, arg=None):
        self._opcode = opcode
        self._arg = arg

    @property
    def opcode(self):
        """Gets the opcode for this instruction."""
        return self._opcode

    @property
    def arg(self):
        """Gets the argument for this instruction. May be None."""
        return self._arg

    def __str__(self):
        """Returns a string representing this instruction.

        It is in the form "OPCODE" if there is no argument and "OPCODE ARG" if
        there is an argument.
        """
        if self._arg is not None:
            return "{0} {1}".format(self._opcode, self._arg)
        else:
            return "{0}".format(self._opcode)

class Parser(object):
    """Constructs and validates the program from the raw data input."""

    def __init__(self):
        self._program = Program()

    @property
    def program(self):
        """Gets the constructed program.

        Program will be empty until parse_data is run.
        Program is not guaranteed to be valid until validate_program is run.
        """
        return self._program
    
    def parse_data(self, data):
        """Takes the raw data as input and constructs a Program

        First, it strips comments. Then it will split the source on whitespace
        to create an array of tokens. Note, even if a label doesn't have
        whitespace between it and the following instruction in the source,
        we ensure it does before splitting. After the token array it created,
        we parse it to construct the resulting program.

        After running this, if an error has not occurred, the program will
        be stored as self.program. Note, the program has not been validated
        until you run validate_program. Until then, the program is not
        guaranteed to be legal.

        Args:
            data: A string of the raw source code.
        """
        # First, remove the comments
        data = self._strip_comments(data)

        # Ensure labels have a space after them
        data = data.replace(':', ': ') 

        # Next, split into a token array
        token_array = data.split()

        # Counter into our token_array
        token_i = 0
        
        # Each time we add an instruction to the list, increment this.
        # This helps determine which instruction a label points to, e.g.
        # if the first line of the program is a label, then it means set
        # the program counter to instruction 0 when jumped to
        instruction_counter = 0

        while token_i < len(token_array):
            # If opcode is one of the four opcodes that take arguments,
            # add an Instruction with the next token as an arg to the program.
            if self._has_arg(token_array[token_i]):
                opcode = token_array[token_i]
                arg = token_array[token_i+1]
                self._program.addInstruction(Instruction(opcode, arg))

                token_i += 1 # Advance an extra element. We don't want to look at the arg next.
                instruction_counter += 1

            # If we make it this far, it means the opcode does not have an argument
            # following it, so just add it as a bare instruction.
            elif self._is_opcode_valid(token_array[token_i]):
                opcode = token_array[token_i]
                self._program.addInstruction(Instruction(opcode))

                instruction_counter += 1

            # If it's a label, add the label and current instruction counter
            # into the label map.
            elif ':' in token_array[token_i]:
                # strip __LABEL__ and insert label name into hashmap
                label = token_array[token_i].replace(':', '')
                self._is_label_valid(label)
                self._program.addLabel(label, instruction_counter)

            # If we've made it this far, the instruction instruction is not valid, so exit
            else:
                print_error("Invalid opcode '{0}', exiting.".format(token_array[token_i]))

            token_i += 1

    def validate_program(self):
        """Verifies parsed program is legal.

        This function will check that:
            ildc has an integral argument,
            the jump instructions have an argument,
            those jump arguments are valid and defined labels.

        This function will not check that:
            the opcodes are valid
        because that has already been verified during the initial parse.
        """
        for instruction in self._program.instructions:
            if self._has_arg(instruction.opcode):
                if instruction.opcode == 'ildc':
                    if instruction.arg is None:
                        print_error("ildc must have an argument.")
                    try:
                        int(instruction.arg) # ildc's argument must be a valid int
                    except:
                        print_error("Invalid immediate number '{0}', exiting".format(instruction.arg))
                else:
                    self._is_label_valid(instruction.arg) # check to see whether label is formatted correctly
                    if self._program.labels.get(instruction.arg) is None: # check to see if the label is mapped to an index
                        print_error("Label '{0}' not found, exiting".format(instruction.arg))
                print_debug(instruction)

    @staticmethod
    def _has_arg(opcode):
        """Tests that the input opcode has an argument

        Args:
            opcode: The opcode to test, as a string.

        Returns:
            True if the input opcode has an arugment. False otherwise.
        """
        return opcode == 'ildc' or opcode == 'jz' or opcode == 'jnz' or opcode == 'jmp'

    @staticmethod
    def _is_opcode_valid(opcode):
        """Tests that the input opcode is valid

        Args:
            opcode: The opcode to test, as a string.

        Returns:
            True if the input opcode is valid. False otherwise.
        """
        return opcode == 'iadd' or opcode == 'isub' or opcode == 'imul' or opcode == 'idiv' or opcode == 'imod' \
        or opcode == 'pop' or opcode == 'dup' or opcode == 'swap' or opcode == 'load' or opcode == 'store' \
        or opcode == 'ildc' or opcode == 'jz' or opcode == 'jnz' or opcode == 'jmp'

    @staticmethod
    def _is_label_valid(label):
        """Ensures the label is syntactically valid.

        A valid label must begin with an alphabetic character then be followed
        by 0 or more alphanumeric or '_' characters. A regular expression for
        valid labels is such: [a-zA-Z][a-zA-Z0-9_]*

        Note, even if the label is valid, that does not guarantee it is defined.

        Returns:
            True if the label is valid as described above. False otherwise.
        """
        if label is None:
            print_error("Jump-style instructions must have an argument.")

        if not label[0].isalpha(): # Ensure first character is alpha
            print_error("Label '{0}' must begin with an alphabetic character, exiting.".format(label))

        for char in label:
            if not char.isalnum() and char != '_': # Ensure character alphanum, or an underscore, De Morgan's law FTW
                print_error("Label '{0}' can only contain alphanumeric characters and '_', exiting.".format(label))

    @staticmethod
    def _strip_comments(raw_data):
        """Strips the comments out of the source code.

        Comments begin with a '#' character and end at the next new line or EOF.
        """
        # The last \n is optional so that comments on the last line are
        # still removed. Note that in python the optional qualifier is greedy,
        # so newlines will still be consumed if present
        return re.sub(r"#.*\n?", '\n', raw_data)
    
def print_debug(input_string):
    if False: # set to True to print debug statements, False to not print anything
        print(input_string)

def print_error(error_string):
    print('Error: {0}'.format(error_string), file=sys.stderr)
    sys.exit(1)

if __name__ == "__main__":
    data = sys.stdin.read() # Data is a string of the input program

    parser = Parser()
    parser.parse_data(data) # Construct the program
    parser.validate_program() # Verify program before running it

    result = parser.program.execute() # Finally execute
    print("Final value is: {0}".format(result))