
import sys

# TODO:
# Document functions
# Remove debugging print statements

class StackClass:
    def __init__(self):
        self.items = []

    def print_stack(self):
        print(self.items)

    def push(self, value):
        print('Pushing ' + str(value))
        self.items.append(int(value))

    def pop(self):
        print('Was ' + str(self.items))
        if len(self.items) == 0:
            print('Error: stack is empty, exiting')
            sys.exit()
        ret=self.items[len(self.items) - 1]
        print('Popping ' + str(ret))
        self.items.pop()
        print('Now ' + str(self.items))
        return ret

    def peek(self):
        if len(self.items) == 0:
            print('Error: stack is empty, exiting')
            sys.exit()
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
    #print(len(token_array))
    while x < len(token_array):
        #print('token: ' + token_array[x])

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
            #print('label found')
            # strip __LABEL__ and insert label name into hashmap
            labels[token_array[x].replace('__LABEL__', '')] = instrs
            #print(labels)

        # if we've made it this far, the instruction instruction is not valid, so quit
        else:
            print('Error: invalid opcode \'' + token_array[x] + '\', exiting') # todo, return something bad here
            sys.exit()
        #print(ret)
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
    print('rec ' + label)
    try:
        print('got: ' + str(jump_addrs[label]))
    except:
        print('bad')
        return -1
    return jump_addrs[label]

# this is the actual interpreter
def run_instructions(instruction_array, jump_addrs):
    pc = 0 # pc is 0, run the 0th index instruction_array
    s = StackClass() # make our stack
    store = {} # make our store
    while pc < len(instruction_array):
        print(len(instruction_array[pc]))
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
            print('jz found')
            top=s.pop()
            if top == 0:
                pc = get_jump_addr(instruction_array[pc][1], jump_addrs) # set pc to what the label is mapped to
                continue

        elif op == 'jnz':
            print('jnz found')
            top=s.pop()
            if top != 0:
                pc = get_jump_addr(instruction_array[pc][1], jump_addrs) # set pc to what the label is mapped to
                continue

        elif op == 'jmp':
            print('jmp found')
            pc = get_jump_addr(instruction_array[pc][1], jump_addrs) # set pc to what the label is mapped to
            continue

        elif op == 'load':
            print('load found')
            addr = s.pop()
            print(addr)
            if addr not in store.keys():
                print('Error: store address ' + str(addr) + ' not initialized, exiting')
                sys.exit()
            print(addr not in store.keys())
            print(store[addr])
            val = store[addr]
            s.push(val)

        elif op == 'store':
            print('store found')
            val = s.pop()
            addr = s.pop()
            store[addr] = val
            print(store)

        elif op == 'TEST':
            s.print_stack()

        else:
            print('Instruction not found ' + op)
            sys.exit()

        s.print_stack()
        pc = pc + 1 # advance to next instruction after current one is completed.
                    # after pc is set with a jump instruction, it in continued
                    # so we never make it here if instruction is jump

    print('final val: ' + str(s.peek()))

# verifies program is correct before continuing onto the interpreter
def is_program_valid(instruction_array, label_map):
    i = 0
    while i < len(instruction_array):
        #print(instruction_array[i])
        if has_arg(instruction_array[i][0]):
            if instruction_array[i][0] == 'ildc':
                try:
                    int(instruction_array[i][1]) # see whether ildc's argument is a valid int
                except:
                    print('Error: invalid digit \'' + instruction_array[i][1] + '\', exiting')
                    sys.exit()
            else:
                is_label_correct(instruction_array[i][1]) # check to see whether label is formatted correctly
                if get_jump_addr(instruction_array[i][1], label_map) < 0: # check to see if the label is mapped to an index
                    print('Error: label \'' + instruction_array[i][1] + '\' not found, exiting')
                    sys.exit()
            print(instruction_array[i])
        i = i + 1
    return True

def strip_comments(raw_data):
    in_comment = False
    ret = ''
    #print('fin + ' + raw_data)
    for char in raw_data:
        #print(char)
        if char == '#': # if we encounter a comment, set in_comment to true
            print('comment found')
            in_comment = True

        if char == '\n': # if we encounter a newline, set in_comment to false
            print('newline found')
            in_comment = False

        if in_comment == False: # if we are not in a comment, append the character to ret
                                # this means that comments are NOT appended to ret, so they are stripped
            ret += char

    #print('fin + ' + ret)
    return ret

def is_label_correct(label):
    if label[0].isalpha() == False: # ensure first character is alpha
        print('Error: label \'' + label + '\' must begin with an alphabetic character, exiting')
        sys.exit()
    for i in label:
        if i.isalnum() == False and i != '_': # ensure character alphanum, or an underscore, De Morgan's law FTW
            print('Error: label \'' + label + '\' can only contain alphanumeric characters and \'_\', exiting')
            sys.exit()

label_map = {}
data = sys.stdin.read()
#print(data)
data=strip_comments(data)
#print(data)
#parse_line(sys.stdin.read())
data = data.replace(':', '__LABEL__ ')
#print(data.split())
instruction_array = parse_all(data.split(), label_map)
#print(instruction_array)
#print(label_map)
is_program_valid(instruction_array, label_map)
run_instructions(instruction_array, label_map)
