import ast

instr_list = []

# global vars that hold label objects for different expressions / statements
current_loop_continue_label = None # this holds the label to the continue of a loop (for -> update, while -> cond)
current_enter_then_label = None # holds the entrance of a loop, or the then part of if-stmt
current_break_out_else_label = None # holds the loop's out, or else part of an if-stmt
# if we're in an if stmt where:
#
# if (x < y && x == z) {
#   x++;
# } else {
#   x--;
# }
# then if x < y BinaryExpr evals to false, we know to jump to the else branch
# and use the label called 'current_break_out_else_label'
# similarly, if we're in a loop where:
#
# while (x < y || x < z) {
#   x++;
# }
#
# if x < y evals to true, jump into the body of the loop
# which is the label held by current_enter_then_label

static_field_offset = 0
non_static_field_offset = 0

# walks up a class' hierarchy and assigns each non-static field a
# unique offset. at end, it sets the class' size to the field_offset
def calc_nonstatic_offsets(cls):
    global non_static_field_offset

    if cls.superclass is not None:
        calc_nonstatic_offsets(cls.superclass)

    for field in cls.fields.viewvalues():
        if field.storage == 'instance':
            field.offset = non_static_field_offset
            non_static_field_offset += 1

    cls.size = non_static_field_offset

def calc_static_offsets(cls):
    global static_field_offset
    for field in cls.fields.viewvalues():
        if field.storage == 'static':
            field.offset = static_field_offset
            static_field_offset += 1

def preprocess(cls):

    global non_static_field_offset

    calc_static_offsets(cls)

    non_static_field_offset = 0
    calc_nonstatic_offsets(cls)

def generate_code(classtable):

    for cls in classtable.viewvalues():
        preprocess(cls)

    instr_list.append('.static_data ' + str(static_field_offset))

    for cls in classtable.viewvalues():
        generate_class_code(cls)

def generate_class_code(cls):

    for method in cls.methods:
        Method(method.name, method.id)
        gen_code(method.body)
    for constr in cls.constructors:
        Constructor(constr.id)
        gen_code(constr.body)

def free_reg():
    ret = ast.var_reg
    ast.var_reg += 1
    return ret

class Procedure:
    def __init__(self, op, arg = None):
        self.opcode = op
        self.arg = arg

        instr_list.append(self)

    def __str__(self):
        if self.arg is None:
            return "{}".format(self.opcode)
        else:
            return "{} {}".format(self.opcode, self.arg)

class Convert:
    def __init__(self, op, reg):
        self.op = op
        self.src = reg
        self.dst = Register()

        instr_list.append(self)

    def __str__(self):
        return "{} {}, {}".format(self.op, self.dst, self.src)

class Register:
    def __init__(self, reg_type='t', reg_num=None):
        self.reg_type = reg_type
        self.reg_num = reg_num

        if self.reg_num == None and self.reg_type != 'sap':
            self.reg_num = free_reg()

    def __str__(self):
        if self.reg_type == 'sap':
            return "{}".format(self.reg_type)
        else:
            return "{}{}".format(self.reg_type, self.reg_num)

class BranchInstr:
    def __init__(self, opcode, label=None, reg=None):
        self.op = opcode
        self.reg = reg
        self.jmp_label = label

        instr_list.append(self)

    def __str__(self):
        if self.jmp_label is None:
            return self.op
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

class Constructor:
    def __init__(self, id):
        self.id = id

        instr_list.append(self)

    def __str__(self):
        return "C_{}:".format(self.id)

class Label:
    def __init__(self, lines, name):
        self.lines = lines
        self.name = str(self.lines) + '_' + str(name)

    def add_to_instr(self):
        instr_list.append(self)

    def __str__(self):
        return "L{}".format(self.name)

class MoveInstr:
    def __init__(self, opcode, reg1, val, val_is_const=False):
        self.op = opcode
        self.dst = reg1
        self.src = val
        self.is_src_const = val_is_const

        instr_list.append(self)

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

class HeapInstr:
    def __init__(self, opcode, reg1, reg2, reg3 = None):
        self.op = opcode
        self.dst = reg1
        self.src1 = reg2
        self.src2 = reg3

        instr_list.append(self)

    def __str__(self):
        if self.src2 is None:
            return "{} {}, {}".format(self.op, self.dst, self.src1)
        else:
            return "{} {}, {}, {}".format(self.op, self.dst, self.src1, self.src2)

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
        # TODO: why don't the types from the typechecker persist here?
        #if (str(stmt.lhs.type) == 'float') and (str(stmt.rhs.type) == 'int'):
        #    conv = Convert('itof', stmt.rhs.end_reg, False)
        #    stmt.rhs.end_reg = conv.dst

        if not isinstance(stmt.lhs, ast.FieldAccessExpr):
            MoveInstr('move', stmt.lhs.end_reg, stmt.rhs.end_reg)
        else:
            HeapInstr('hstore', stmt.lhs.base.end_reg, stmt.lhs.offset_reg, stmt.rhs.end_reg)

    elif isinstance(stmt, ast.VarExpr):
        stmt.end_reg = stmt.var.reg

    elif isinstance(stmt, ast.ConstantExpr):
        if stmt.kind == 'int':
            reg = Register()
            MoveInstr('move_immed_i', reg, stmt.int, True)
        elif stmt.kind == 'float':
            reg = Register()
            MoveInstr('move_immed_f', reg, stmt.float, True)
        elif stmt.kind == 'string':
            pass

        stmt.end_reg = reg

    elif isinstance(stmt, ast.BinaryExpr):

        global current_break_out_else_label, current_enter_then_label

        gen_code(stmt.arg1)
        gen_code(stmt.arg2)

        if stmt.arg1.end_reg and stmt.arg2.end_reg:
            reg = Register()
            if (stmt.bop != 'and') and (stmt.bop != 'or'):
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

            if (stmt.bop == 'and'):
                MoveInstr('move_immed_i', reg, 1, True)
                BranchInstr('bz', current_break_out_else_label, stmt.arg1.end_reg)
                BranchInstr('bz', current_break_out_else_label, stmt.arg2.end_reg)

            if (stmt.bop == 'or'):
                MoveInstr('move_immed_i', reg, 0, True)
                BranchInstr('bnz', current_enter_then_label, stmt.arg1.end_reg)
                BranchInstr('bnz', current_enter_then_label, stmt.arg2.end_reg)

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
        current_enter_then_label = entry_label = Label(stmt.lines, 'FOR_ENTRY')
        current_loop_continue_label = continue_label = Label(stmt.lines, 'FOR_UPDATE')
        current_break_out_else_label = out_label = Label(stmt.lines, 'FOR_OUT')

        cond_label.add_to_instr()

        gen_code(stmt.cond)
        BranchInstr('bz', out_label, stmt.cond.end_reg)

        entry_label.add_to_instr()
        gen_code(stmt.body)

        continue_label.add_to_instr()
        gen_code(stmt.update)

        BranchInstr('jmp', cond_label)

        out_label.add_to_instr()

    elif isinstance(stmt, ast.AutoExpr):

        gen_code(stmt.arg)

        if stmt.when == 'post':
            tmp_reg = Register()
            MoveInstr('move', tmp_reg, stmt.arg.end_reg)

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

        gen_code(stmt.expr)

        # Load the result into a0
        MoveInstr('move', Register('a', 0), stmt.expr.end_reg)

        # TODO: Make sure everything is popped off the stack

        # Return to caller
        BranchInstr('ret')

    elif isinstance(stmt, ast.WhileStmt):

        current_loop_continue_label = cond_label = Label(stmt.lines, 'WHILE_COND')
        current_enter_then_label = entry_label = Label(stmt.lines, 'WHILE_ENTRY')
        current_break_out_else_label = out_label = Label(stmt.lines, 'WHILE_OUT')

        cond_label.add_to_instr()

        gen_code(stmt.cond)

        BranchInstr('bz', out_label, stmt.cond.end_reg)

        entry_label.add_to_instr()

        gen_code(stmt.body)

        BranchInstr('jmp', cond_label)

        out_label.add_to_instr()

    elif isinstance(stmt, ast.BreakStmt):
        global current_break_out_else_label
        BranchInstr('jmp', current_break_out_else_label)

    elif isinstance(stmt, ast.ContinueStmt):
        global current_loop_continue_label
        BranchInstr('jmp', current_loop_continue_label)

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

        current_enter_then_label = then_part = Label(stmt.lines, 'THEN_PART')
        current_break_out_else_label = else_part = Label(stmt.lines, 'ELSE_PART')
        out_label = Label(stmt.lines, 'IF_STMT_OUT')

        gen_code(stmt.condition)

        BranchInstr('bnz', else_part, stmt.condition.end_reg)

        then_part.add_to_instr()
        gen_code(stmt.thenpart)

        BranchInstr('jmp', out_label)

        else_part.add_to_instr()

        gen_code(stmt.elsepart)

        out_label.add_to_instr()

    elif isinstance(stmt, ast.FieldAccessExpr):

        gen_code(stmt.base)

        cls = ast.lookup(ast.classtable, stmt.base.type.typename)
        field = ast.lookup(cls.fields, stmt.fname)

        offset_reg = Register()
        ret_reg = Register()

        MoveInstr('move_immed_i', offset_reg, field.offset, True)
        HeapInstr('hload', ret_reg, stmt.base.end_reg, offset_reg)

        stmt.offset_reg = offset_reg
        stmt.end_reg = ret_reg

    elif isinstance(stmt, ast.ClassReferenceExpr):
        stmt.end_reg = Register('sap')

    elif isinstance(stmt, ast.NewObjectExpr):
        recd_addr = Register()
        size_reg = Register()
        MoveInstr('move_immed_i', size_reg, stmt.classref.size, True)
        HeapInstr('halloc', recd_addr, size_reg)
        # TODO: save regs, put args into arg regs
        Procedure('call', 'C_' + str(stmt.constr_id))
        # TODO: pop saved regs off stack
        stmt.end_reg = recd_addr

    else:
        print 'need instance ' + str(type(stmt))
