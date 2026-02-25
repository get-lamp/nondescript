from src.lang.base import Constant


class String(str, Constant):
    def __init__(self, string, pos=(None, None)):
        super().__init__(string, pos)

    def __new__(cls, *args, **kw):
        string, pos = args
        return super().__new__(cls, string)

    def eval(self):
        return str(self)


class Float(float, Constant):
    def __init__(self, number, pos=(None, None)):
        super().__init__(number, pos)

    def __new__(cls, *args, **kw):
        number, pos = args
        return super().__new__(cls, number)

    def eval(self):
        return self


class Integer(int, Constant):
    def __init__(self, number, pos=(None, None)):
        super().__init__(number, pos)

    def __new__(cls, *args, **kwarg):
        # allow for not instantiating with the position tuple
        number, pos = args if len(args) == 2 else (*args, None)
        return super().__new__(cls, number)

    def eval(self):
        return self


class Bool(Constant):
    def __init__(self, word, pos=(None, None)):
        super().__init__(word, pos)

    def eval(self):

        return any([self.word is True, (type(self.word) is str) and self.word.lower() == "true", self.word == 1])

    # identifiers
