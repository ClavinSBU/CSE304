
import sys, re

# TODO:
# Check that labels are valid even when not jumped to
#   E.g. the following should be invalid
#       2here:    ildc 10
#                 ildc 20
#   Currently, it passes

class StackClass:
    def __init__(self):
        self.items = []

    def get_stack(self):
        return self.items

    def push(self, value):
        print_debug('Pushing ' + str(value))
        self.items.append(int(value))

    def pop(self):
        print_debug('Was ' + str(self.items))
        if len(self.items) == 0:
            print_error("Stack is empty, exiting")
        ret=self.items[len(self.items) - 1]
        print_debug('Popping ' + str(ret))
        self.items.pop()
        print_debug('Now ' + str(self.items))
        return ret

    def peek(self):
        if len(self.items) == 0:
            print_error("Stack is empty, exiting")
        return self.items[len(self.items) - 1]

# boolean function to see if it's one of the 4 opcodes that come with an argument after it
def has_arg(opcode):
    if opcode == 'ildc' or opcode == 'jz' or opcode == 'jnz' or opcode == 'jmp':
        return True
    return False

# check to see whether the opcode is one that is valid
def is_valid_opcode(opcode):
    if opcode == 'iadd' or opcode == 'isub' or opcode == 'imul' or opcode == 'idiv' or opcode == 'imod' \
    or opcode == 'pop' or opcode == 'dup' or opcode == 'swap' or opcode == 'load' or opcode == 'store':
        return True
    return False

# this takes the inputted program and returns a list of instructions to be run by the interpreter
def parse_all(token_array, labels):
    x = 0
    instrs = 0 # each time we add an instruction to the list, increment this.
               # this helps determine which instruction a label points to, i.e.
               # if the first line of the program is a label, then it means set
               # program counter to instruction 0 when jumped to
    ret = []
    #print_debug(len(token_array))
    while x < len(token_array):
        #print_debug('token: ' + token_array[x])

        # if opcode is one of the four opcodes that take arguments, append the list (opcode and arg) to the array
        if has_arg(token_array[x]):
            ret.append([token_array[x], token_array[x + 1]])
            x = x + 1 # advance two elements as the argument would be the next, which is not what we want
            instrs = instrs + 1 # we've added an instruction, so increment our counter

        # if we make it this far, it means the opcode does not have an argument following it, so just append it ret
        elif is_valid_opcode(token_array[x]):
            ret.append([token_array[x]]) # add it to instruction list
            instrs = instrs + 1 # we've added an instruction, so increment our counter

        # if it's a jump instruction, insert the label into the hashmap where <label name> points to current instr count
        elif '__LABEL__' in token_array[x]:
            #print_debug('label found')
            # strip __LABEL__ and insert label name into hashmap
            labels[token_array[x].replace('__LABEL__', '')] = instrs
            #print_debug(labels)

        # if we've made it this far, the instruction instruction is not valid, so quit
        else:
            print_error("Invalid opcode '{0}', exiting.".format(token_array[x])) # todo, return something bad here
        #print_debug(ret)
        x = x + 1
    return ret

# Math function. Pops the first two elements off and does whatever the operand
# variable says to do as per operand's value, then pushes the result back onto the stack.
def imath(s, operand):

    first=s.pop()
    second=s.pop()

    if operand == '+':
        s.push(first + second)

    elif operand == '-':
        s.push(second - first)

    elif operand == '*':
        s.push(first * second)

    elif operand == '/':
        s.push(second / first)

    elif operand == '%':
        s.push(second % first)

# this function returns the value the program counter should be set to,
# which is determined by what value the label is mapped to in the hashmap
# it returns -1 if it is not found, indicating the label is not part of program.
def get_jump_addr(label, jump_addrs):
    print_debug('rec ' + label)
    if label not in jump_addrs.keys():
        return -1
    return jump_addrs[label]

# this is the actual interpreter
def run_instructions(instruction_array, jump_addrs):
    pc = 0 # pc is 0, run the 0th index instruction_array
    s = StackClass() # make our stack
    store = {} # make our store
    while pc < len(instruction_array):
        print_debug(len(instruction_array[pc]))
        op = instruction_array[pc][0]

        if op == 'ildc':
            s.push(instruction_array[pc][1])

        elif op == 'iadd':
            imath(s, '+') # The add, sub, etc functions all pop the first two elements
                       # and do the desired operation on it, so since they all are
                       # the same except for the actual operation, use one function
                       # and use logic to find out which operation.
        elif op == 'isub':
            imath(s, '-')

        elif op == 'imul':
            imath(s, '*')

        elif op == 'idiv':
            imath(s, '/')

        elif op == 'imod':
            imath(s, '%')

        elif op == 'pop':
            s.pop()

        elif op == 'dup':
            s.push(s.peek())

        elif op == 'swap':
            first=s.pop()
            second=s.pop()
            s.push(first)
            s.push(second)

        elif op == 'jz':
            print_debug('jz found')
            top=s.pop()
            if top == 0:
                pc = get_jump_addr(instruction_array[pc][1], jump_addrs) # set pc to what the label is mapped to
                continue

        elif op == 'jnz':
            print_debug('jnz found')
            top=s.pop()
            if top != 0:
                pc = get_jump_addr(instruction_array[pc][1], jump_addrs) # set pc to what the label is mapped to
                continue

        elif op == 'jmp':
            print_debug('jmp found')
            pc = get_jump_addr(instruction_array[pc][1], jump_addrs) # set pc to what the label is mapped to
            continue

        elif op == 'load':
            print_debug('load found')
            addr = s.pop()
            print_debug(addr)
            if addr not in store.keys():
                print_error("Store address '{0}' not initialized, exiting.".format(addr))
            print_debug(addr not in store.keys())
            print_debug(store[addr])
            val = store[addr]
            s.push(val)

        elif op == 'store':
            print_debug('store found')
            val = s.pop()
            addr = s.pop()
            store[addr] = val
            print_debug(store)

        elif op == 'TEST':
            print_debug(s.get_stack())

        else:
            print_error("Instruction not found '{0}'".format(op))

        print_debug(s.get_stack())
        pc = pc + 1 # advance to next instruction after current one is completed.
                    # after pc is set with a jump instruction, it in continued
                    # so we never make it here if instruction is jump

    print('Final value is: ' + str(s.peek()))

# verifies program is correct before continuing onto the interpreter
def is_program_valid(instruction_array, label_map):
    i = 0
    while i < len(instruction_array):
        #print_debug(instruction_array[i])
        if has_arg(instruction_array[i][0]):
            if instruction_array[i][0] == 'ildc':
                try:
                    int(instruction_array[i][1]) # see whether ildc's argument is a valid int
                except:
                    print_error("Invalid immediate number '{0}', exiting".format(instruction_array[i][1]))
            else:
                is_label_correct(instruction_array[i][1]) # check to see whether label is formatted correctly
                if get_jump_addr(instruction_array[i][1], label_map) < 0: # check to see if the label is mapped to an index
                    print_error("Label '{0}' not found, exiting".format(instruction_array[i][1]))
            print_debug(instruction_array[i])
        i = i + 1
    return True

def strip_comments(raw_data):
    return re.sub(r"#.*\n", '\n', raw_data)

def is_label_correct(label):
    if label[0].isalpha() == False: # ensure first character is alpha
        print_error("Label '{0}' must begin with an alphabetic character, exiting.".format(label))
    for i in label:
        if i.isalnum() == False and i != '_': # ensure character alphanum, or an underscore, De Morgan's law FTW
            print_error("Label '{0}' can only contain alphanumeric characters and '_', exiting.".format(label))

def print_debug(input_string):
    if 0: # set to 1 to print debug statements, 0 to not print anything
        print(input_string)

def print_error(error_string):
    print('Error: {0}'.format(error_string))
    sys.exit(1)

label_map = {} # hashmap to map labels to their respective program counter values
data = sys.stdin.read() # data is a string of the inputted program

#print_debug(data)

data=strip_comments(data) # remove comments from inputted source

#print_debug(data)
#parse_line(sys.stdin.read())

data = data.replace(':', '__LABEL__ ') # replace labels with a reserved keyword for labels

#print_debug(data.split())

instruction_array = parse_all(data.split(), label_map) # create formatted list of instructions to be run on interpreter

#print_debug(instruction_array)
#print_debug(label_map)

is_program_valid(instruction_array, label_map) # verify program is going to run on interpreter
run_instructions(instruction_array, label_map) # run it
