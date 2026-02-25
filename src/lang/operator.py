from src.lang.base import Operator, UnaryOperator, UnaryPostOperator


class Not(UnaryOperator):
    def eval(self, scope, arguments, interp):
        return not interp.getval(interp.eval(arguments))


class Increment(UnaryPostOperator):
    def eval(self, scope, arguments=None, interp=None):
        scope[arguments.word] += 1
        return scope[arguments.word]


class Decrement(UnaryPostOperator):
    def eval(self, scope, arguments=None, interp=None):
        scope[arguments.word] -= 1
        return scope[arguments.word]


class Assign(Operator):
    def eval(self, left, right, heap):
        heap[left.word] = right
        return left


class Equal(Operator):
    def eval(self, left, right, scope):
        return left == right


class Unequal(Operator):
    def eval(self, left, right, scope):
        return left != right


class EqualStrict(Operator):
    pass


class UnequalStrict(Operator):
    pass


class Greater(Operator):
    def eval(self, left, right, scope):
        return left > right


class Lesser(Operator):
    def eval(self, left, right, scope):
        return left < right


class Or(Operator):
    def eval(self, left, right, scope):
        return left or right


class Nor(Operator):
    def eval(self, left, right, scope):
        return not (left or right)


class Xor(Operator):
    def eval(self, left, right, scope):
        return left ^ right


class And(Operator):
    def eval(self, left, right, scope):
        return left and right


class Nand(Operator):
    def eval(self, left, right, scope):
        return not (left and right)


class Subtract(Operator):
    def eval(self, left, right, scope):
        return left - right


class Add(Operator):
    def eval(self, left, right, scope):
        return left + right


class Divide(Operator):
    def eval(self, left, right, scope):
        return left / right


class Multiply(Operator):
    def eval(self, left, right, scope):
        return left * right
