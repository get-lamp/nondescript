import re

import src.lang.base
from src.lang.base import (
    Lexeme,
    CLAUSE,
    COMMA,
    EXPRESSION,
    INCLUDE,
    OP,
    PARAMETER,
    PRNT,
    WAIT,
    Space,
    Delimiter,
    Keyword,
    Identifier,
    NewLine,
    Tab,
    Bracket,
    Parentheses,
    DoubleQuote,
    SingleQuote,
)

from src.lang import control
from src.lang import data
from src.lang import operator as op


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
        r_space: lambda t: Space(t),
        r_newline: lambda t: NewLine(t),
        r_tab: lambda t: Tab(t),
        r_bracket_l: lambda t: Bracket(t, open=True),
        r_bracket_r: lambda t: Bracket(t, open=False),
        r_double_quote: lambda t: DoubleQuote(t),
        r_single_quote: lambda t: SingleQuote(t),
        r_parentheses_l: lambda t: Parentheses(t, open=True),
        r_parentheses_r: lambda t: Parentheses(t, open=False),
        r_slash: {
            r_asterisk: lambda t: Lang.CommentBlock(t, open=True),
            r_slash: lambda t: Lang.CommentLine(t),
            None: lambda t: op.Divide(t),
        },
        r_asterisk: {
            r_slash: lambda t: Lang.CommentBlock(t, open=False),
            None: lambda t: op.Multiply(t),
        },
        r_comma: lambda t: src.lang.base.Comma(t),
        r_bang: {
            r_equal: {
                r_equal: {None: lambda t: op.UnequalStrict(t)},
                None: lambda t: op.Unequal(t),
            },
            None: lambda t: op.Not(t),
        },
        r_equal: {
            r_equal: {
                r_equal: {None: lambda t: op.EqualStrict(t)},
                None: lambda t: op.Equal(t),
            },
            None: lambda t: op.Assign(t),
        },
        r_plus: {
            r_plus: lambda t: op.Increment(t),
            None: lambda t: op.Add(t),
        },
        r_float: lambda t: data.Float(t),
        r_int: lambda t: data.Integer(t),
        r_dash: {
            r_dash: lambda t: op.Decrement(t),
            r_float: lambda t: data.Float(t),
            r_int: lambda t: data.Integer(t),
            None: lambda t: op.Subtract(t),
        },
        r_greater: lambda t: op.Greater(t),
        r_lesser: lambda t: op.Lesser(t),
        r_or: lambda t: op.Or(t),
        r_nor: lambda t: op.Nor(t),
        r_xor: lambda t: op.Xor(t),
        r_and: lambda t: op.And(t),
        r_nand: lambda t: op.Nand(t),
        r_not: lambda t: op.Not(t),
        r_true: lambda t: data.Bool(t),
        r_false: lambda t: data.Bool(t),
        r_identifier: lambda t: Lang.identifier(t),
    }

    keywords = {
        "prnt": lambda t: Lang.Prnt(t),
        "if": lambda t: control.If(t),
        "else": lambda t: control.Else(t),
        "end": lambda t: control.End(t),
        "for": lambda t: control.For(t),
        "procedure": lambda t: control.Procedure(t),
        "def": lambda t: control.Def(t),
        "exec": lambda t: control.Exec(t),
        "include": lambda t: Lang.Include(t),
        "WAIT": lambda t: Lang.Wait(t),
    }

    parameters = {
        "UNTIL": lambda t: Lang.Until(t),
        "BY": lambda t: Lang.By(t),
    }

    clause = {r"<parameter>": lambda: Lang.expression}

    expression = {
        r"<unary-op>": lambda: Lang.expression,
        r"<delim>": lambda: Lang.expression,
        r"<bracket>": lambda: Lang.expression[r"<const>|<ident>"],
        r"<const>|<ident>": {
            r"<bracket>|<const>|<ident>": lambda: Lang.expression[r"<const>|<ident>"],
            OP: lambda: Lang.expression,
            r"<unary-post-op>": lambda: Lang.expression,
            "</delim>|</bracket>": lambda: Lang.expression[r"<const>|<ident>"],
            COMMA: lambda: Lang.expression,
        },
    }

    @staticmethod
    def identifier(t):
        if t.word in Lang.keywords:
            return Lang.keywords[t.word](t)
        elif t.word in Lang.parameters:
            return Lang.parameters[t.word](t)
        else:
            return Identifier(t)

    @staticmethod
    def bind_keyword(keyword, cls):
        Lang.keywords["keyword"] = lambda t: cls(t)

    class Parameter(Lexeme):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

        def eval(self, scope, arguments=None, interp=None):
            return interp.eval(arguments)

        @staticmethod
        def type():
            return PARAMETER

        def __repr__(self):
            return PARAMETER

    class Until(Parameter):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

    class By(Parameter):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

    class Wait(Keyword):
        @staticmethod
        def type():
            return WAIT

        def parse(self, parser, **kwargs):
            self.condition = parser.build_ast(parser.parse_expression())
            self.until = parser.build_ast(parser.clause(Lang.Until))
            return [self, self.condition, self.until]

        def eval(self, interp, expression):
            c = interp.eval(self.condition)
            u = interp.eval(self.until)
            print("WAITING %s UNTIL %s" % (c, u))

        def __repr__(self):
            return WAIT

    class Prnt(Keyword):
        @staticmethod
        def type():
            return PRNT

        def parse(self, parser, **kwargs):
            self.text = parser.build_ast(parser.parse_expression())
            return [self, self.text]

        def eval(self, interp, expression):
            result = interp.eval(expression)
            while isinstance(result, list) and len(result) == 1:
                result = result[0]
            print(result)

        def __repr__(self):
            return PRNT

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
            return INCLUDE

        def parse(self, parser, **kwargs):
            src = parser.parse_expression()
            return [self, src]

        def eval(self, interp, source):
            print(source)
            exit(1)

    class Grammar(list):
        def __init__(self, rules):
            self.grammar = rules
            self.legal = rules
            super().__init__()

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
                self.legal = (
                    self.legal[ll] if not callable(self.legal[ll]) else self.legal[ll]()
                )
                super().append(i)
                return self

            # close
            return False

    class Clause(Grammar):
        @staticmethod
        def type():
            return CLAUSE

    class Expression(Grammar):
        def __init__(self):
            super().__init__(Lang.expression)

        def type(self):
            return EXPRESSION
