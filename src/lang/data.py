from src.lang.base import LIST, Lexeme, STRUCT, CONST


class Constant(Lexeme):
    @staticmethod
    def type():
        return CONST

    def __repr__(self):
        return "<const %s>" % self.word


class String(str, Constant):
    def __init__(self, token, **kwargs):
        Constant.__init__(self, token, **kwargs)

    def __new__(cls, token, **kwargs):
        return str.__new__(cls, token.word)

    def eval(self):
        return str(self)


class Float(float, Constant):
    def __init__(self, token, **kwargs):
        Constant.__init__(self, token, **kwargs)

    def __new__(cls, token, **kwargs):
        return float.__new__(cls, token.word)

    def eval(self):
        return self


class Integer(int, Constant):
    def __init__(self, token, **kwargs):
        Constant.__init__(self, token, **kwargs)

    def __new__(cls, token, **kwargs):
        return int.__new__(cls, token.word)

    def eval(self):
        return self


class Bool(Constant):
    def __init__(self, token, **kwargs):
        super().__init__(token, **kwargs)

    def eval(self):
        return any(
            [
                self.word is True,
                (type(self.word) is str) and self.word.lower() == "true",
                self.word == 1,
            ]
        )


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
