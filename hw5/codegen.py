import ast

instr_list = []
current_loop_cond_label = None
current_break_out_label = None

def free_reg():
    ret = ast.var_reg
    ast.var_reg += 1
    return ret

class Convert:
    def __init__(self, op, reg, to_int):
        self.op = op
        self.src = reg
        if to_int:
            self.dst = Register()
        else:
            self.dst = Register('f')

        instr_list.append(self)

    def __str__(self):
        return "{} {}, {}".format(self.op, self.dst, self.src)

class Register:
    def __init__(self, reg_type = 't', reg_num = None):
        self.reg_type = reg_type
        self.reg_num = reg_num

        if self.reg_num == None:
            self.reg_num = free_reg()

    def __str__(self):
        return "{}{}".format(self.reg_type, self.reg_num)

class BranchInstr:
    def __init__(self, opcode, label, reg = None):
        self.op = opcode
        self.reg = reg
        self.jmp_label = label

        instr_list.append(self)

    def __str__(self):
        if self.reg is None:
            return "{} {}".format(self.op, self.jmp_label)
        else:
            return "{} {} {}{}".format(self.op, self.jmp_label, self.reg.reg_type, self.reg.reg_num)

class Method:
    def __init__(self, name, id):
        self.name = name
        self.id = id

        instr_list.append(self)

    def __str__(self):
        return "M_{}_{}:".format(self.name, self.id)

class Label:
    def __init__(self, lines, name):
        self.lines = lines
        self.name = str(self.lines) + '_' + str(name)

    def add_to_instr(self):
        instr_list.append(self)

    def __str__(self):
        return "L{}".format(self.name)

class MoveInstr:
    def __init__(self, opcode, reg1, val, val_is_const = False):
        self.op = opcode
        self.dst = reg1
        self.src = val
        self.is_src_const = val_is_const

        instr_list.append(self)

    # is_src_const helps determine whether to put the 't' before the last arg.
    # if it's a constant, there's no 't' as it's not a reg, it's the actual value
    def __str__(self):
        return "{} {}, {}".format(self.op, self.dst, self.src)

class ArithInstr:
    def __init__(self, opcode, reg1, reg2, reg3):
        self.op = 'i' + str(opcode)
        self.dst = reg1
        self.src1 = reg2
        self.src2 = reg3

        instr_list.append(self)

    def __str__(self):
        return "{} {}, {}, {}".format(self.op, self.dst, self.src1, self.src2)


def generate_code(classtable):
    for cls in classtable.viewvalues():
        generate_class_code(cls)

def generate_class_code(cls):

    for method in cls.methods:
        method.is_method = True
        gen_code(method)
        #stmt_error(method.body)
        gen_code(method.body)
    for constr in cls.constructors:
        current_method = method
        #stmt_error(method.body)
        gen_code(constr.body)

def gen_code(stmt):

    # stmt.end_reg is the destination register for each expression
    stmt.end_reg = None

    if isinstance(stmt, ast.BlockStmt):
        for stmt_line in stmt.stmtlist:
            gen_code(stmt_line)

    elif isinstance(stmt, ast.ExprStmt):
        gen_code(stmt.expr)

    elif isinstance(stmt, ast.AssignExpr):
        gen_code(stmt.rhs)
        gen_code(stmt.lhs)
        if (str(stmt.lhs.type) == 'float') and (str(stmt.rhs.type) == 'int'):
            conv = Convert('itof', stmt.rhs.end_reg, False)
            stmt.rhs.end_reg = conv.dst
        MoveInstr('move', stmt.lhs.end_reg, stmt.rhs.end_reg)

    elif isinstance(stmt, ast.VarExpr):
        #stmt.end_reg = stmt.var.reg
        stmt.end_reg = stmt.var.reg

    elif isinstance(stmt, ast.ConstantExpr):
        #reg = free_reg()
        if stmt.kind == 'int':
            reg = Register()
            MoveInstr('move_immed_i', reg, stmt.int, True)
        elif stmt.kind == 'float':
            reg = Register('f')
            MoveInstr('move_immed_f', reg, stmt.float, True)
        elif stmt.kind == 'string':
            pass

        stmt.end_reg = reg

    elif isinstance(stmt, ast.BinaryExpr):

        gen_code(stmt.arg1)
        gen_code(stmt.arg2)

        if stmt.arg1.end_reg and stmt.arg2.end_reg:
            #reg = free_reg()
            reg = Register()
            ArithInstr('sub' if (stmt.bop == 'eq') or (stmt.bop == 'neq') else stmt.bop, reg,
                    stmt.arg1.end_reg, stmt.arg2.end_reg)

            if (stmt.bop == 'eq'):

                # check if r2 == r3
                # 1. perform sub r1, r2, r3 (done above)
                # 2. branch to set_one if r1 is zero
                # 3. else, fall through and set r1 to zero
                # 4. jump out so we don't set r1 to one by accident

                ieq_set = Label(stmt.lines, 'SET_EQ')
                ieq_out = Label(stmt.lines, 'SET_EQ_OUT')

                BranchInstr('bz', ieq_set, reg)
                MoveInstr('move_immed_i', reg, 0, True)
                BranchInstr('jmp', ieq_out)
                
                ieq_set.add_to_instr()
                MoveInstr('move_immed_i', reg, 1, True)

                ieq_out.add_to_instr()

            stmt.end_reg = reg

    elif isinstance(stmt, ast.ForStmt):

        # for-loop:
        # for (i = 0; i < 10; i++) {
        #   body
        # }

        # set i's reg equal to 0
        # create a label after this, as this is where we jump back to at end of loop
        # also create the 'out' label which is what we jump to when breaking out of loop
        # generate code for the 'cond' (test if i's reg is less than 10's reg)
        # test if the cond evaluated to false with 'bz', if so, break out of loop
        # else, fall through into the body of the for-loop
        # when body is over, generate code to update the var (i++)
        # jump unconditionally back to the cond_label, where we eval if i is still < 10
        gen_code(stmt.init)

        cond_label = Label(stmt.lines, 'FOR_COND')
        current_loop_cond_label = cond_label
        out_label = Label(stmt.lines, 'FOR_OUT')
        current_break_out_label = out_label

        cond_label.add_to_instr()

        gen_code(stmt.cond)
        BranchInstr('bz', out_label, stmt.cond.end_reg)

        gen_code(stmt.body)
        gen_code(stmt.update)

        BranchInstr('jmp', cond_label)

        out_label.add_to_instr()

    elif isinstance(stmt, ast.AutoExpr):

        gen_code(stmt.arg)

        if stmt.when == 'post':
            #tmp_reg = free_reg()
            tmp_reg = Register()
            MoveInstr('move', tmp_reg, stmt.arg.end_reg)

        #one_reg = free_reg()
        one_reg = Register()

        # Load 1 into a register
        MoveInstr('move_immed_i', one_reg, 1, True)

        ArithInstr('add' if stmt.oper == 'inc' else 'sub', stmt.arg.end_reg, stmt.arg.end_reg, one_reg)

        if stmt.when == 'post':
            stmt.end_reg = tmp_reg
        else:
            stmt.end_reg = stmt.arg.end_reg

    elif isinstance(stmt, ast.SkipStmt):
        pass

    elif isinstance(stmt, ast.ReturnStmt):
        pass

    elif isinstance(stmt, ast.WhileStmt):

        cond_label = Label(stmt.lines, 'WHILE_COND')
        current_loop_cond_label = cond_label
        cond_label.add_to_instr()
        out_label = Label(stmt.lines, 'WHILE_OUT')

        current_break_out_label = out_label

        gen_code(stmt.cond)

        BranchInstr('bz', out_label, stmt.cond.end_reg)

        gen_code(stmt.body)

        BranchInstr('jmp', cond_label)

        out_label.add_to_instr()

    elif isinstance(stmt, ast.BreakStmt):
        global current_break_out_label
        BranchInstr('jmp', current_break_out_label)

    elif isinstance(stmt, ast.ContinueStmt):
        global current_loop_cond_label
        BranchInstr('jmp', current_loop_cond_label)

    elif isinstance(stmt, ast.IfStmt):

        # if (x == y)
        #   ++x;
        # else
        #   --x;

        # generate 2 labels, for the else part, and the out part
        # test if x == y
        # if not true, jump to the else part
        # if true, we're falling through to the then part, then must jump
        # out right before hitting the else part straight to the out part

        then_part = Label(stmt.lines, 'THEN_PART')
        else_part = Label(stmt.lines, 'ELSE_PART')
        out_label = Label(stmt.lines, 'IF_STMT_OUT')

        gen_code(stmt.condition)

        BranchInstr('bnz', else_part, stmt.condition.end_reg)

        then_part.add_to_instr()
        gen_code(stmt.thenpart)

        BranchInstr('jmp', out_label)

        else_part.add_to_instr()

        gen_code(stmt.elsepart)

        out_label.add_to_instr()

    elif stmt.is_method:
        Method(stmt.name, stmt.id)

    else:
        print 'need instance ' + str(type(stmt))
