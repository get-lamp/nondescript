import re

# 	TODO
# weird delimiter characters behavior
# check for Evaluable & Callable classes


class Lang:
    delimiters = r"[\"\':!,;+*^&@#$%&\-\\/\|=$()?<>\s\[\]]"

    r_space = r"[ ]"
    r_newline = r"[\n;]"
    r_tab = r"[\t]"
    r_slash = r"[/]"
    r_asterisk = r"[*]"
    r_comma = r"[,]"
    r_equal = r"[=]"
    r_plus = r"[+]"
    r_dash = r"[-]"
    r_greater = r"[>]"
    r_lesser = r"[<]"
    r_bracket_l = r"[\[]"
    r_bracket_r = r"[\]]"
    r_parentheses_l = r"[(]"
    r_parentheses_r = r"[)]"
    r_hash = r"[#]"
    r_bang = r"[!]"
    r_question = r"[?]"
    r_double_quote = r"[\"]"
    r_single_quote = r"[\']"
    r_float = r"^[0-9]*\.[0-9]+$"
    r_int = r"^[0-9]+$"
    r_or = r"(?i)^OR"
    r_nor = r"(?i)^NOR"
    r_xor = r"(?i)^XOR"
    r_and = r"(?i)^AND$"
    r_nand = r"(?i)^NAND$"
    r_not = r"(?i)^NOT$"
    r_true = r"(?i)^TRUE$"
    r_false = r"(?i)^FALSE$"
    r_identifier = r"[_a-zA-Z][_a-zA-Z0-9]*"

    # Will try to match greedily
    symbols = {
        r_space: lambda w, t: Lang.Space(w, t),
        r_newline: lambda w, t: Lang.NewLine(w, t),
        r_tab: lambda w, t: Lang.Tab(w, t),
        r_bracket_l: lambda w, t: Lang.Bracket(w, t, open=True),
        r_bracket_r: lambda w, t: Lang.Bracket(w, t, open=False),
        r_double_quote: lambda w, t: Lang.DoubleQuote(w, t),
        r_single_quote: lambda w, t: Lang.SingleQuote(w, t),
        r_parentheses_l: lambda w, t: Lang.Parentheses(w, t, open=True),
        r_parentheses_r: lambda w, t: Lang.Parentheses(w, t, open=False),
        r_slash: {
            r_asterisk: lambda w, t: Lang.CommentBlock(w, t, open=True),
            r_slash: lambda w, t: Lang.CommentLine(w, t),
            None: lambda w, t: Lang.Divide(w, t),
        },
        r_asterisk: {
            r_slash: lambda w, t: Lang.CommentBlock(w, t, open=False),
            None: lambda w, t: Lang.Multiply(w, t),
        },
        r_comma: lambda w, t: Lang.Comma(w, t),
        r_bang: {
            r_equal: {
                r_equal: {None: lambda w, t: Lang.UnequalStrict(w, t)},
                None: lambda w, t: Lang.Unequal(w, t),
            },
            None: lambda w, t: Lang.Not(w, t),
        },
        r_equal: {
            r_equal: {
                r_equal: {None: lambda w, t: Lang.EqualStrict(w, t)},
                None: lambda w, t: Lang.Equal(w, t),
            },
            None: lambda w, t: Lang.Assign(w, t),
        },
        r_plus: {
            r_plus: lambda w, t: Lang.Increment(w, t),
            None: lambda w, t: Lang.Add(w, t),
        },
        r_float: lambda w, t: Lang.Float(w, t),
        r_int: lambda w, t: Lang.Integer(w, t),
        r_dash: {
            r_dash: lambda w, t: Lang.Decrement(w, t),
            r_float: lambda w, t: Lang.Float(w, t),
            r_int: lambda w, t: Lang.Integer(w, t),
            None: lambda w, t: Lang.Subtract(w, t),
        },
        r_greater: lambda w, t: Lang.Greater(w, t),
        r_lesser: lambda w, t: Lang.Lesser(w, t),
        r_or: lambda w, t: Lang.Or(w, t),
        r_nor: lambda w, t: Lang.Nor(w, t),
        r_xor: lambda w, t: Lang.Xor(w, t),
        r_and: lambda w, t: Lang.And(w, t),
        r_nand: lambda w, t: Lang.Nand(w, t),
        r_not: lambda w, t: Lang.Not(w, t),
        r_true: lambda w, t: Lang.Bool(w, t),
        r_false: lambda w, t: Lang.Bool(w, t),
        r_identifier: lambda w, t: Lang.identifier(w, t),
    }

    keywords = {
        "prnt": lambda w, t: Lang.Prnt(w, t),
        "if": lambda w, t: Lang.If(w, t),
        "else": lambda w, t: Lang.Else(w, t),
        "end": lambda w, t: Lang.End(w, t),
        "for": lambda w, t: Lang.For(w, t),
        "procedure": lambda w, t: Lang.Procedure(w, t),
        "def": lambda w, t: Lang.Def(w, t),
        "exec": lambda w, t: Lang.Exec(w, t),
        "include": lambda w, t: Lang.Include(w, t),
        "WAIT": lambda w, t: Lang.Wait(w, t),
    }

    parameters = {
        "UNTIL": lambda w, t: Lang.Until(w, t),
        "BY": lambda w, t: Lang.By(w, t),
    }

    clause = {r"<parameter>": lambda: Lang.expression}

    expression = {
        r"<unary-op>": lambda: Lang.expression,
        r"<delim>": lambda: Lang.expression,
        r"<bracket>": lambda: Lang.expression[r"<const>|<ident>"],
        r"<const>|<ident>": {
            r"<bracket>|<const>|<ident>": lambda: Lang.expression[r"<const>|<ident>"],
            "<op>": lambda: Lang.expression,
            r"<unary-post-op>": lambda: Lang.expression,
            "</delim>|</bracket>": lambda: Lang.expression[r"<const>|<ident>"],
            "<comma>": lambda: Lang.expression,
        },
    }

    @staticmethod
    def identifier(w, t):
        if w in Lang.keywords:
            return Lang.keywords[w](w, t)
        elif w in Lang.parameters:
            return Lang.parameters[w](w, t)
        else:
            return Lang.Identifier(w, t)

    @staticmethod
    def bind_keyword(keyword, cls):
        Lang.keywords["keyword"] = lambda w, t: cls(w, t)

    class Evaluable:
        pass

    class Callable:
        def get_signature(self):
            return self.signature

    # keywords
    class Block:
        def __init__(self, *args, **kwargs):
            self.length = 0
            self.owner = None

    class Control:
        pass

    class Lexeme:
        """
        Base class for every language word
        """

        def __init__(self, word, pos=(None, None), **kwargs):
            self.word = word
            self.line, self.char = pos
            self.set(kwargs)

        def set(self, kwargs):
            """
            Convenience method for setting properties dynamically
            """
            for i in kwargs:
                setattr(self, i, kwargs[i])

        @staticmethod
        def type():
            raise NotImplementedError

        def parse(self, parser, **kwargs):
            raise NotImplementedError

        def __repr__(self):
            return "<%s><%s>" % (self.__class__.__name__, self.word)

        def __eq__(self, other):
            return all(
                [
                    self.word == other.word,
                    self.line == other.line,
                    self.char == other.char,
                ]
            )

    class WhiteSpace(Lexeme):
        """
        Spaces and tabs
        """

        pass

    class Space(WhiteSpace):
        pass

    class NewLine(WhiteSpace):

        @staticmethod
        def type():
            return "<newline>"

    class Tab(WhiteSpace):
        pass

    # base types
    class Vector(Lexeme):
        @staticmethod
        def type():
            return "<struct>"

    class Constant(Lexeme):
        @staticmethod
        def type():
            return "<const>"

        def __repr__(self):
            return "<const %s>" % self.word

    class String(str, Constant):
        def __init__(self, string, pos=(None, None)):
            super(Lang.String, self).__init__(string, pos)

        def __new__(cls, *args, **kw):
            string, pos = args
            return super(Lang.String, cls).__new__(cls, string)

        def eval(self):
            return str(self)

    class Float(float, Constant):
        def __init__(self, number, pos=(None, None)):
            super(Lang.Float, self).__init__(number, pos)

        def __new__(cls, *args, **kw):
            number, pos = args
            return super(Lang.Float, cls).__new__(cls, number)

        def eval(self):
            return self

    class Integer(int, Constant):
        def __init__(self, number, pos=(None, None)):
            super(Lang.Integer, self).__init__(number, pos)

        def __new__(cls, *args, **kwarg):
            # allow for not instantiating with the position tuple
            number, pos = args if len(args) == 2 else (*args, None)
            return super(Lang.Integer, cls).__new__(cls, number)

        def eval(self):
            return self

    class Bool(Constant):
        def __init__(self, word, pos=(None, None)):
            super().__init__(word, pos)

        def eval(self):

            return any([self.word is True, (type(self.word) is str) and self.word.lower() == "true", self.word == 1])

    class List(list, Vector):
        def __init__(self, lst=None):
            list.__init__(self, lst if lst else [])

        @staticmethod
        def type():
            return "<list>"

        def __add__(self, other):
            return Lang.List(list.__add__(self, other))

        def __getitem__(self, item):
            result = list.__getitem__(self, item)
            try:
                return Lang.List(result)
            except TypeError:
                return result

        def eval(self):
            return self

    # operators
    class Operator(Lexeme):
        @staticmethod
        def type():
            return "<op>"

        def __repr__(self):
            return "<op %s>" % self.word

        def eval(self, *args):
            raise NotImplementedError

    class UnaryOperator(Operator):
        @staticmethod
        def type():
            return "<unary-op>"

        def __repr__(self):
            return "<unary-op %s>" % self.word

        def eval(self, *arg):
            raise NotImplementedError

    class Not(UnaryOperator):
        def eval(self, scope, arguments, interp):
            return not interp.getval(interp.eval(arguments))

    class UnaryPostOperator(Operator):
        @staticmethod
        def type():
            return "<unary-post-op>"

        def __repr__(self):
            return "<unary-post-op %s>" % self.word

        def eval(self, *arg):
            raise NotImplementedError

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

    # delimiters
    class Delimiter(Lexeme):
        pass

    # expression delimiters
    class Parentheses(Delimiter):
        def __init__(self, *args, open: bool = True, **kwargs):
            self.open = open
            super().__init__(*args, **kwargs)

        def type(self):
            return "<delim>" if self.open else "</delim>"

        def __repr__(self):
            return "<delim>" if self.open else "</delim>"

    class Bracket(Delimiter):
        def __init__(self, *args, open: bool = True, **kwargs):
            self.open = open
            super().__init__(*args, **kwargs)

        def type(self):
            return "<bracket>" if self.open else "</bracket>"

        def __repr__(self):
            return "<bracket>" if self.open else "</bracket>"

    # list delimiter
    class Comma(Delimiter):
        @staticmethod
        def type():
            return "<comma>"

        def __repr__(self):
            return "<comma>"

    # string delimiters
    class DoubleQuote(Delimiter):
        @staticmethod
        def type():
            return "<d-quote>"

        def __repr__(self):
            return "<d-quote>"

    class SingleQuote(Delimiter):
        @staticmethod
        def type():
            return "<s-quote>"

        def __repr__(self):
            return "<s-quote>"

    # identifiers
    class Identifier(Lexeme):
        @staticmethod
        def type():
            return "<ident>"

        def eval(self, scope, arguments=None, interp=None):
            v = scope.get(self.word, None)
            if arguments is not None and v is not None:
                return v.call(arguments, interp)
            else:
                return v

    class Keyword(Lexeme):
        def get_identifier(self):
            return self.identifier

        @staticmethod
        def type():
            return "<keyword>"

        def __repr__(self):
            return "<keyword %s>" % (self.word)

    class Procedure(Keyword, Callable, Block, Control):
        def __init__(self, word, pos=(None, None), **kwargs):
            self.address = None
            self.identifier = None
            self.signature = Lang.List()
            super(Lang.Procedure, self).__init__(word, pos=(None, None), **kwargs)

        @staticmethod
        def type():
            return "<procedure>"

        def parse(self, parser, **kwargs):
            print("Procedure is being parsed")

            # parse identifier
            i = parser.next()
            if not isinstance(i, Lang.Identifier):
                raise Exception("Procedure must have an identifier")
            else:
                self.identifier = [i]

            try:
                # get arguments
                self.signature = parser.build(parser.expression())

            except Exception:
                self.signature = Lang.List()

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
                self.signature = Lang.List()

            # get function block
            self.block = parser.block(until=Lang.End)

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
            return "<exec>"

        def parse(self, parser, **kwargs):

            identifier = [parser.next()]

            try:
                arguments = parser.build(parser.expression())
            except Exception:
                arguments = Lang.List()

            return [self, identifier, arguments]

        def eval(self, interp, signature):

            # get arguments if any
            arguments = interp.eval(signature.pop()) if len(signature) > 1 else []

            # get identifier from instruction line
            identifier = interp.getval(signature.pop(), ref=True)

            # get procedure from scope
            routine = interp.fetch(identifier)

            if not isinstance(routine, Lang.Callable):
                raise Exception("Not a callable object")

            return interp.call(routine, arguments)

    class Main(Block):
        @staticmethod
        def type():
            return "<main>"

    class If(Keyword, Block, Control):

        @staticmethod
        def type():
            return "<if>"

        def parse(self, parser, **kwargs):
            # store condition pre-built
            condition = parser.build(parser.expression(until=Lang.NewLine))
            return [self, condition]

        def eval(self, interp, expr):
            # if condition is truthy, interpreter executes the following block
            interp.push_read_enabled(bool(interp.eval(expr)))
            interp.push_block(self)

    class Else(Keyword, Control):
        @staticmethod
        def type():
            return "<else>"

        def parse(self, parser, **kwargs):
            return [self]

        @staticmethod
        def eval(interp, expr):
            # if last block was executed following will not, and vice versa
            interp.toggle_read_enabled()

    class End(Keyword, Control, Delimiter):
        @staticmethod
        def type():
            return "<end>"

        def parse(self, parser, **kwargs):
            return [self]

        @staticmethod
        def eval(interp, expr):

            block = interp.block()

            if isinstance(block, Lang.If):
                interp.endif()

            elif isinstance(block, Lang.For):
                interp.end_for()

            elif isinstance(block, Lang.Procedure):
                interp.end_call()

            elif isinstance(block, Lang.Def):
                interp.end_call()
            else:
                raise Exception("Unknown block type")

    class For(Keyword, Block, Control):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.initializer = None
            self.condition = None
            self.increment = None

        @staticmethod
        def type():
            return "<for>"

        def parse(self, parser, **kwargs):
            # store condition pre-built
            parser.build(parser.expression(until=Lang.NewLine))
            parser.build(parser.expression(until=Lang.NewLine))
            parser.build(parser.expression(until=Lang.NewLine))
            return [self, self.initializer, self.condition, self.increment]

        def eval(self, interp, args):
            # if condition is truthy, interpreter executes the following block
            self.initializer = args[0]
            self.condition = args[1]
            self.increment = args[2]

            # run initialize
            interp.eval(self.initializer)
            interp.push_read_enabled(bool(interp.eval(self.condition)))
            interp.push_block(self)

    class Parameter(Lexeme):
        def __init__(self, *args, **kwargs):
            super(Lang.Parameter, self).__init__(*args, **kwargs)

        def eval(self, scope, arguments=None, interp=None):
            return interp.eval(arguments)

        @staticmethod
        def type():
            return "<parameter>"

        def __repr__(self):
            return "<parameter>"

    class Until(Parameter):
        def __init__(self, *args, **kwargs):
            super(Lang.Until, self).__init__(*args, **kwargs)

    class By(Parameter):
        def __init__(self, *args, **kwargs):
            super(Lang.By, self).__init__(*args, **kwargs)

    class Wait(Keyword):
        @staticmethod
        def type():
            return "<wait>"

        def parse(self, parser, **kwargs):
            self.condition = parser.build(parser.expression())
            self.until = parser.build(parser.clause(Lang.Until))
            return [self, self.condition, self.until]

        def eval(self, interp, expression):
            c = interp.eval(self.condition)
            u = interp.eval(self.until)
            print("WAITING %s UNTIL %s" % (c, u))

        def __repr__(self):
            return "<wait>"

    class Prnt(Keyword):
        @staticmethod
        def type():
            return "<prnt>"

        def parse(self, parser, **kwargs):
            self.text = parser.build(parser.expression())
            return [self, self.text]

        def eval(self, interp, expression):
            result = interp.eval(expression)
            while isinstance(result, list) and len(result) == 1:
                result = result[0]
            print(result)

        def __repr__(self):
            return "<prnt>"

    """
    PREPROCESSOR
    
    """

    class Preprocessor(Lexeme):
        pass

    class CommentBlock(Preprocessor, Delimiter):
        pass

    class CommentLine(Preprocessor, Delimiter):
        pass

    class Include(Preprocessor, Keyword):
        @staticmethod
        def type():
            return "<include>"

        def parse(self, parser, **kwargs):
            src = parser.expression()
            return [self, src]

        def eval(self, interp, source):
            print(source)
            exit(1)

    class Grammar(list):
        def __init__(self, rules):
            self.grammar = rules
            self.legal = rules
            super(Lang.Grammar, self).__init__()

        # does lexeme belong to this grammar
        @staticmethod
        def belongs(i, grammar):
            branch = grammar
            # iterate through currently legal words
            for r in branch:
                if re.match(r, i.type()):
                    return True
                elif branch.get(r, None) is not None:
                    branch = branch[r] if not callable(branch[r]) else branch[r]()

            return False

        @staticmethod
        def is_legal(s, grammar):
            rules = grammar
            # iterate through words in sentence
            for i in s:
                # iterate through currently legal words
                found = False
                for r in rules:
                    if re.match(r, i.type()):
                        rules = rules[r] if not callable(rules[r]) else rules[r]()
                        found = True
                        break

                if not found:
                    return False
            return True

        def hint(self):
            if self.legal is None:
                return None
            else:
                return self.legal.keys()

        def can_push(self, i):
            # iterate through currently legal words
            for r in self.legal:
                if re.match(r, i.type()):
                    return r
            return False

        def push(self, i):
            # if instruction begins, legal should point to all instruction set
            if len(self) == 0:
                self.legal = self.grammar

            ll = self.can_push(i)
            # print('Is legal %s? %s %s %s' % (self.__class__.__name__, i.type(), self.hint(), l))
            # push term
            if ll:
                # climb up in grammar tree
                self.legal = self.legal[ll] if not callable(self.legal[ll]) else self.legal[ll]()
                super(Lang.Grammar, self).append(i)
                return self

            # close
            return False

    class Clause(Grammar):
        def type(self):
            return "<clause>"

    class Expression(Grammar):
        def __init__(self):
            super(Lang.Expression, self).__init__(Lang.expression)

        def type(self):
            return "<expression>"
