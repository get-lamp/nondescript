from abc import ABC

import src.lang.base
import src.lang.data
from src.lang.base import Keyword, IF, ELSE, END, FOR, PROCEDURE, Identifier, EXEC, Delimiter


class Block:
    def __init__(self, *args, **kwargs):
        self.length = 0
        self.owner = None


class Control:
    pass


class If(Keyword, Block, Control):
    @staticmethod
    def type():
        return IF

    def parse(self, parser, **kwargs):
        # store condition pre-built
        condition = parser.build(parser.expression(until=src.lang.base.NewLine))
        return [self, condition]

    def eval(self, interp, expr):
        # if condition is truthy, interpreter executes the following block
        interp.push_read_enabled(bool(interp.eval(expr)))
        interp.push_block(self)


class Else(Keyword, Control):
    @staticmethod
    def type():
        return ELSE

    def parse(self, parser, **kwargs):
        return [self]

    @staticmethod
    def eval(interp, expr):
        # if last block was executed following will not, and vice versa
        interp.toggle_read_enabled()


class For(Keyword, Block, Control):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.init = None
        self.condition = None
        self.increment = None
        self.address = None

    @staticmethod
    def type():
        return FOR

    def parse(self, parser, **kwargs):
        # store condition pre-built
        self.init = parser.build(parser.expression(until=src.lang.base.NewLine))
        self.condition = parser.build(parser.expression(until=src.lang.base.NewLine))
        self.increment = parser.build(parser.expression(until=src.lang.base.NewLine))
        return [self]

    def eval(self, interp):
        # if condition is truthy, interpreter executes the following block

        self.address = interp.pntr
        interp.eval(self.init)

        # run initialize
        interp.push_read_enabled(bool(interp.eval(self.condition)))
        interp.push_block(self)


class Callable(ABC):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.signature = None

    def get_signature(self):
        return self.signature


class Procedure(Keyword, Callable, Block, Control):
    def __init__(self, word, pos=(None, None), **kwargs):
        self.address = None
        self.identifier = None
        self.signature = src.lang.data.List()
        super().__init__(word, pos=(None, None), **kwargs)

    @staticmethod
    def type():
        return PROCEDURE

    def parse(self, parser, **kwargs):
        print("Procedure is being parsed")

        # parse identifier
        i = parser.next()
        if not isinstance(i, Identifier):
            raise Exception("Procedure must have an identifier")
        else:
            self.identifier = [i]

        try:
            # get arguments
            self.signature = parser.build(parser.expression())

        except Exception:
            self.signature = src.lang.data.List()

        return [self, self.identifier, self.signature]

    def eval(self, interp, signature):
        print("Procedure is being eval'd")

        # store procedure address
        self.address = interp.pntr

        # eval procedure identifier, leaving room for dynamic procedures
        self.identifier = interp.getval(self.identifier, ref=False)

        # store identifier & memory address
        interp.bind(self.identifier.word, self)

        # skip function block. We are just declaring the function
        interp.move(self.length + 1)

    def call(self):
        raise NotImplementedError()


class Def(Procedure):
    def __init__(self, word, pos=(None, None), **kwargs):
        super().__init__(word, pos=(None, None), **kwargs)
        self.block = []

    def parse(self, parser, **kwargs):
        # parse identifier
        self.identifier = [parser.next()]

        try:
            # get arguments
            self.signature = parser.build(parser.expression())
        except Exception:
            self.signature = src.lang.data.List()

        # get function block
        self.block = parser.block(until=End)

        return [self, self.identifier, self.signature]

    def eval(self, interp, signature):

        # store procedure address
        self.address = interp.pntr

        # eval procedure identifier, leaving room for dynamic procedures
        self.identifier = interp.getval(self.identifier, ref=False)

        # store identifier & memory address
        interp.bind(self.identifier.word, self)

    def call(self, arguments, interp):
        return interp.call(self, arguments)


class Exec(Keyword):
    @staticmethod
    def type():
        return EXEC

    def parse(self, parser, **kwargs):

        identifier = [parser.next()]

        try:
            arguments = parser.build(parser.expression())
        except Exception:
            arguments = src.lang.data.List()

        return [self, identifier, arguments]

    def eval(self, interp, signature):

        # get arguments if any
        arguments = interp.eval(signature.pop()) if len(signature) > 1 else []

        # get identifier from instruction line
        identifier = interp.getval(signature.pop(), ref=True)

        # get procedure from scope
        routine = interp.fetch(identifier)

        if not isinstance(routine, Callable):
            raise Exception("Not a callable object")

        return interp.call(routine, arguments)


class End(Keyword, Control, Delimiter):
    @staticmethod
    def type():
        return END

    def parse(self, parser, **kwargs):
        return [self]

    @staticmethod
    def eval(interp, expr):

        block = interp.block()

        if isinstance(block, If):
            interp.endif()

        elif isinstance(block, For):
            interp.end_for(block.address, block.condition, block.increment)

        elif isinstance(block, Procedure):
            interp.end_call()

        elif isinstance(block, Def):
            interp.end_call()
        else:
            raise Exception("Unknown block type")
