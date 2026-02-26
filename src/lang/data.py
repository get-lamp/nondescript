from src.lang.base import LIST, Lexeme, STRUCT, CONST


class Constant(Lexeme):
    @staticmethod
    def type():
        return CONST

    def __repr__(self):
        return "<const %s>" % self.word


class String(str, Constant):
    def __init__(self, string, *args, **kwargs):
        super().__init__(string, *args, **kwargs)

    def __new__(cls, *args, **kwargs):
        string, pos = args
        return super().__new__(cls, string)

    def eval(self):
        return str(self)


class Float(float, Constant):
    def __init__(self, number, *args, **kwargs):
        super().__init__(number, *args, **kwargs)

    def __new__(cls, *args, **kw):
        number, pos = args
        return super().__new__(cls, number)

    def eval(self):
        return self


class Integer(int, Constant):
    def __init__(self, number, *args, **kwargs):
        super().__init__(number, *args, **kwargs)

    def __new__(cls, *args, **kwarg):
        # allow for not instantiating with the position tuple
        number, pos = args if len(args) == 2 else (*args, None)
        return super().__new__(cls, number)

    def eval(self):
        return self


class Bool(Constant):
    def __init__(self, word, *args, **kwargs):
        super().__init__(word, *args, **kwargs)

    def eval(self):
        return any([self.word is True, (type(self.word) is str) and self.word.lower() == "true", self.word == 1])


class Vector(Lexeme):
    @staticmethod
    def type():
        return STRUCT


class List(list, Vector):
    def __init__(self, lst=None):
        list.__init__(self, lst if lst else [])

    @staticmethod
    def type():
        return LIST

    def __add__(self, other):
        return List(list.__add__(self, other))

    def __getitem__(self, item):
        result = list.__getitem__(self, item)
        try:
            return List(result)
        except TypeError:
            return result

    def eval(self):
        return self
