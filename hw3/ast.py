class DecafClass(object):
    class_table = []

    def __init__(self, name, super_class_name=None):
        self._name = name
        self._super_class = super_class_name
        self._fields = []
        self._methods = []
        self._constructors = []

        DecafClass.class_table.append(self)

    @property
    def name(self):
        return self._name

    @property
    def super_class(self):
        if self._super_class is None:
            return ""
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

    def add_field(self, field):
        self._fields.append(field)

    def add_method(self, method):
        self._methods.append(method)

    def add_constructor(self, constructor):
        self._constructors.append(constructor)

    def __str__(self):
        pass  # TODO


class DecafConstructor(object):
    constructor_table = []

    def __init__(self, ident, visibility, parameters, var_table, body):
        self._id = ident
        self._visibility = visibility
        self._parameters = parameters
        self._var_table = var_table
        self._body = body

        DecafConstructor.constructor_table.append(self)

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

    def __str__(self):
        pass  # TODO


class DecafField(object):
    field_table = []

    def __init__(self, name, ident, decaf_class, visibility, applicability,
                 decaf_type):
        self._name = name
        self._id = ident
        self._class = decaf_class
        self._visibility = visibility
        self._applicability = applicability
        self._type = decaf_type

        DecafField.field_table.append(self)

    @property
    def name(self):
        return self._name

    @property
    def id(self):
        return self._id

    @property
    def decaf_class(self):
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

    def __str__(self):
        pass  # TODO


class DecafMethod(object):
    method_table = []

    def __init__(self, name, ident, decaf_class, visibility, applicability,
                 parameters, return_type, var_table, body):
        self._name = name
        self._id = ident
        self._class = decaf_class
        self._visibility = visibility
        self._applicability = applicability
        self._parameters = parameters
        self._return_type = return_type
        self._var_table = var_table
        self._body = body

        DecafMethod.method_table.append(self)

    @property
    def name(self):
        return self._name

    @property
    def id(self):
        return self._id

    @property
    def decaf_class(self):
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

    def __str__(self):
        pass  # TODO


class DecafVariable(object):
    def __init__(self, name, ident, kind, decaf_type):
        self._name = name
        self._id = ident
        self._kind = kind
        self._type = decaf_type

    @property
    def name(self):
        return self._name

    @property
    def id(self):
        return self._id

    @property
    def kind(self):
        return self._kind

    @property
    def type(self):
        return self._type

    def __str__(self):
        pass  # TODO


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
    def user_defined(class_name):
        return DecafType(class_name)

    def __str__(self):
        pass  # TODO
