class DecafClass(object):
    # Stores a list of all classes parsed so far
    table = []

    def __init__(self, name, super_class_name):
        self._name = name
        self._super_class = super_class_name
        self._fields = DecafField.context
        self._methods = DecafMethod.context
        self._constructors = DecafConstructor.context

        # The context list does not make sense for classes, so we just
        # insert the new class into the table list.
        self.table.append(self)

        # Set the classes of all previously seen fields, methods, and tables
        # and flush their context
        DecafConstructor.flush_context(name)
        DecafField.flush_context(name)
        DecafMethod.flush_context(name)

    @property
    def name(self):
        return self._name

    @property
    def super_class(self):
        if self._super_class is None:
            return ''
        else:
            return self._super_class

    @property
    def fields(self):
        return self._fields

    @property
    def methods(self):
        return self._methods

    @property
    def constructors(self):
        return self._constructors

    def __str__(self):
        # Use a list of strings to build the result string. They will be
        # .join()'d later. This is more efficient than concatenating them.
        slist = []
        slist.append('Class Name: {}'.format(self.name))
        slist.append('Superclass Name: {}'.format(self.super_class))
        slist.append('Fields:')
        for field in self.fields:
            slist.append('{}'.format(field))
        slist.append('Constructors:')
        for constructor in self.constructors:
            slist.append('{}'.format(constructor))
        slist.append('Methods:')
        for method in self.methods:
            slist.append('{}'.format(method))
        return '\n'.join(slist)


class DecafConstructor(object):
    __auto_id = 1

    # Stores a list of all constructors belonging to a class already seen.
    table = []
    # Stores a list of all constructors belonging to the class currently being
    # parsed.
    context = []

    def __init__(self, ident, visibility, parameters, var_table, body):
        self._id = ident
        self._visibility = visibility
        self._parameters = parameters
        self._var_table = var_table
        self._body = body

        self.context.append(self)

    @property
    def id(self):
        return self._id

    @property
    def visibility(self):
        return self._visibility

    @property
    def parameters(self):
        return self._parameters

    @property
    def var_table(self):
        return self._var_table

    @property
    def body(self):
        return self._body

    @classmethod
    def get_new_id(cls):
        ident = cls.__auto_id
        cls.__auto_id += 1
        return ident

    @classmethod
    def flush_context(cls, class_name):
        '''Move all constructors from the context list to the table list.'''
        cls.table += cls.context
        cls.context = []

    def __str__(self):
        pass  # TODO


class DecafField(object):
    __auto_id = 1

    # Stores a list of all fields belonging to a class already seen.
    table = []
    # Stores a list of all fields belonging to the class currently being
    # parsed.
    context = []

    def __init__(self, var, visibility, applicability):
        self._name = var.name
        self._id = self.get_new_id()
        self._class = None
        self._visibility = visibility
        self._applicability = applicability
        self._type = var.type

        self.context.append(self)

    @property
    def name(self):
        return self._name

    @property
    def id(self):
        return self._id

    @property
    def decaf_class(self):
        if self._class is None:
            return ''
        else:
            return self._class

    @property
    def visibility(self):
        return self._visibility

    @property
    def applicability(self):
        return self._applicability

    @property
    def decaf_type(self):
        return self._type

    @classmethod
    def flush_context(cls, class_name):
        '''Move all fields from the context list to the table list.

        Also sets the class attributes of those fields'''
        for field in cls.context:
            field._class = class_name
        cls.table += cls.context
        cls.context = []

    @classmethod
    def get_new_id(cls):
        ident = cls.__auto_id
        cls.__auto_id += 1
        return ident

    def __str__(self):
        return ('FIELD {_id}, {_name}, {_class}, {_visibility}, '
                '{_applicability}, {_type}').format(**vars(self))


class DecafMethod(object):
    __auto_id = 1

    # Stores a list of all methods belonging to a class already seen.
    table = []
    # Stores a list of all methods belonging to the class currently being
    # parsed.
    context = []

    def __init__(self, name, visibility, applicability,
                 parameters, return_type, var_table, body):
        self._name = name
        self._id = self.get_new_id()
        self._class = None
        self._visibility = visibility
        self._applicability = applicability
        self._parameters = parameters
        self._return_type = return_type
        self._var_table = var_table
        self._body = body

        self.context.append(self)

    @property
    def name(self):
        return self._name

    @property
    def id(self):
        return self._id

    @property
    def decaf_class(self):
        if self._class is None:
            return ''
        else:
            return self._class

    @property
    def visibility(self):
        return self._visibility

    @property
    def applicability(self):
        return self._applicability

    @property
    def parameters(self):
        return self._parameters

    @property
    def return_type(self):
        return self._return_type

    @property
    def var_table(self):
        return self._var_table

    @property
    def body(self):
        return self._body

    @classmethod
    def flush_context(cls, class_name):
        '''Move all methods from the context list to the table list.

        Also sets the class attributes of those methods.'''
        for method in cls.context:
            method._class = class_name
        cls.table += cls.context
        cls.context = []

    @classmethod
    def get_new_id(cls):
        ident = cls.__auto_id
        cls.__auto_id += 1
        return ident

    def __str__(self):
        # Use a list of strings to build the result string. They will be
        # .join()'d later. This is more efficient than concatenating them.
        slist = []
        slist.append('METHOD: {}, {}, {}, {}, {}, {}'.format(
            self.id, self.name, self.decaf_class, self.visibility,
            self.applicability, self.return_type))
        paramString = ', '.join([str(param)
                                 for param in self.parameters])
        slist.append('Method parameters: {}'.format(paramString))
        if len(self.var_table) > 0:
            # Ensure that there's a newline before the variable table.
            varString = '\n' + '\n'.join([str(var)
                                          for var in self.var_table.values()])
        else:
            varString = ''
        slist.append('Variable Table: {}'.format(varString))
        slist.append('Method Body: {}'.format(stmt_to_string(self.body)))
        return '\n'.join(slist)


class DecafVariable(object):
    '''Represents a variable in the Decaf language.

    This class is used for all variables (formal parameters and local
    variables). It is also used temporarily to construct fields.'''
    __auto_id = 1

    def __init__(self, name):
        '''This should only be used if you need a barebones variable.

        Otherwise, refer to the classmethods local and formal for a more
        complete instantiation method.'''
        self._name = name
        self._id = self.get_new_id()
        self._kind = None
        self._type = None

    @property
    def name(self):
        return self._name

    @property
    def id(self):
        return self._id

    @property
    def kind(self):
        if self._kind is None:
            return ''
        else:
            return self._kind

    @property
    def type(self):
        if self._type is None:
            return ''
        else:
            return self._type

    @type.setter
    def type(self, value):
        self._type = value

    @classmethod
    def get_new_id(cls):
        ident = cls.__auto_id
        cls.__auto_id += 1
        return ident

    @classmethod
    def reset_ids(cls):
        cls.__auto_id = 1

    @classmethod
    def formal(cls, name, decafType):
        '''Create a formal parameter variable.'''
        var = cls(name)
        var._kind = 'formal'
        var._type = decafType
        return var

    @classmethod
    def local(cls, name, decafType):
        '''Create a local variable.'''
        var = cls(name)
        var._kind = 'local'
        var._type = decafType
        return var

    def __str__(self):
        return 'VARIABLE {_id}, {_name}, {_kind}, {_type}'.format(**vars(self))


class DecafType(object):
    def __init__(self, decaftype):
        self._type = decaftype

    @property
    def type(self):
        return self._type

    @staticmethod
    def int():
        return DecafType('int')

    @staticmethod
    def float():
        return DecafType('float')

    @staticmethod
    def boolean():
        return DecafType('boolean')

    @staticmethod
    def string():
        return DecafType('string')

    @staticmethod
    def void():
        return DecafType('void')

    @staticmethod
    def user_defined(class_name):
        return DecafType('user({})'.format(class_name))

    def __str__(self):
        return self.type


def stmt_to_string(stmt):
    return ''  # TODO


def initAST():
    '''Construct the initial AST for every program.

    According to the Decaf specification, every program has access to two
    built-in classes: In and Out.

    In has:
    - public static int scan_int()
    - public static float scan_float()

    Out has:
    - public static void print(int i)
    - public static void print(float f)
    - public static void print(boolean b)
    - public static void print(string s)'''
    # Construct the type we'll need
    intType = DecafType.int()
    floatType = DecafType.float()
    voidType = DecafType.void()
    boolType = DecafType.boolean()
    strType = DecafType.string()

    body = ()

    # Construct the methods for In
    DecafMethod('scan_int', 'public', 'static', [], intType, {}, body)
    DecafMethod('scan_float', 'public', 'static', [], floatType, {}, body)

    # Construct the In class
    DecafClass('In', None)

    # Construct the methods for Out
    intVar = DecafVariable.formal('i', intType)
    DecafMethod('print', 'public', 'static', [intVar], voidType, {'i': intVar},
                body)
    DecafVariable.reset_ids()

    floatVar = DecafVariable.formal('f', floatType)
    DecafMethod('print', 'public', 'static', [floatVar], voidType,
                {'f': floatVar}, body)
    DecafVariable.reset_ids()

    boolVar = DecafVariable.formal('b', boolType)
    DecafMethod('print', 'public', 'static', [boolVar], voidType,
                {'b': boolVar}, body)
    DecafVariable.reset_ids()

    strVar = DecafVariable.formal('s', strType)
    DecafMethod('print', 'public', 'static', [strVar], voidType, {'s': strVar},
                body)
    DecafVariable.reset_ids()

    # Construct the Out class
    DecafClass('Out', None)
