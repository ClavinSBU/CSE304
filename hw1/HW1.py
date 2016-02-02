
import sys

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
        ret=self.items[len(self.items) - 1]
        print('Popping ' + str(ret))
        self.items.pop()
        print('Now ' + str(self.items))
        return ret

    def peek(self):
        return self.items[len(self.items) - 1]

def has_arg(opcode):
    if opcode == 'ildc' or opcode == 'jz' or opcode == 'jnz' or opcode == 'jmp':
        return True
    return False

def is_valid_opcode(opcode):
    if opcode == 'iadd' or opcode == 'isub' or opcode == 'imul' or opcode == 'idiv' or opcode == 'imod' \
    or opcode == 'pop' or opcode == 'dup' or opcode == 'swap' or opcode == 'load' or opcode == 'store':
        return True
    return False

def parse_all(token_array, labels):
    x = 0
    instrs = 0
    ret = []
    #print(len(token_array))
    while x < len(token_array):
        #print('token: ' + token_array[x])
        # if opcode is one of the four opcodes that take arguments, append the list (opcode and arg) to the array
        if has_arg(token_array[x]):
            ret.append([token_array[x], token_array[x + 1]])
            x = x + 1 # advance two elements as the argument would be the next, which is not what we want
            instrs = instrs + 1
        elif is_valid_opcode(token_array[x]):
            ret.append([token_array[x]])
            instrs = instrs + 1
        elif '__LABEL__' in token_array[x]:
            #print('label found')
            # strip __LABEL__ and insert label name into hashmap
            labels[token_array[x].replace('__LABEL__', '')] = instrs
            #print(labels)
        else:
            print('invalid opcode ' + token_array[x]) # todo, return something bad here
        #print(ret)
        x = x + 1
    return ret

# Math function. Pops the first two elements off and does whatever the operand
# variable says to do, then pushes the result back onto the stack.
def imath(s, operand):

    first=s.pop()
    second=s.pop()

    if operand == '+':
        s.push(first + second)

    elif operand == '-':
        s.push(first - second)

    elif operand == '*':
        s.push(first * second)

    elif operand == '/':
        s.push(first / second)

    elif operand == '%':
        s.push(first % second)

def get_jump_addr(label, jump_addrs):
    print('rec ' + label)
    print('got: ' + str(jump_addrs[label]))
    return jump_addrs[label]

def run_instructions(instruction_array, jump_addrs):
    pc = 0
    s = StackClass()
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
                pc = get_jump_addr(instruction_array[pc][1], jump_addrs)
                continue

        elif op == 'jnz':
            print('jnz found')
            top=s.pop()
            if top != 0:
                pc = get_jump_addr(instruction_array[pc][1], jump_addrs)
                continue

        elif op == 'jmp':
            print('jmp found')
            pc = get_jump_addr(instruction_array[pc][1], jump_addrs)
            continue

        elif op == 'TEST':
            s.print_stack()

        else:
            print('Instruction not found ' + op)

        pc = pc + 1

    print('final val: ' + str(s.peek()))

label_map = {}
data = sys.stdin.read()
#parse_line(sys.stdin.read())
data = data.replace(':', '__LABEL__ ')
print(data.split())
instruction_array = parse_all(data.split(), label_map)
print(instruction_array)
#print(label_map)
run_instructions(instruction_array, label_map)
