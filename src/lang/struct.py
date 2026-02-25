from src.lang.base import Vector, LIST


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
