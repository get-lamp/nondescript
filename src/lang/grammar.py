import re

import src.lang.base
from src.lang.base import (
    Lexeme,
    CLAUSE,
    COMMA,
    EXPRESSION,
    INCLUDE,
    MAIN,
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
from src.lang.control import Block

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
        r_space: lambda w, t: Space(w, t),
        r_newline: lambda w, t: NewLine(w, t),
        r_tab: lambda w, t: Tab(w, t),
        r_bracket_l: lambda w, t: Bracket(w, t, open=True),
        r_bracket_r: lambda w, t: Bracket(w, t, open=False),
        r_double_quote: lambda w, t: DoubleQuote(w, t),
        r_single_quote: lambda w, t: SingleQuote(w, t),
        r_parentheses_l: lambda w, t: Parentheses(w, t, open=True),
        r_parentheses_r: lambda w, t: Parentheses(w, t, open=False),
        r_slash: {
            r_asterisk: lambda w, t: Lang.CommentBlock(w, t, open=True),
            r_slash: lambda w, t: Lang.CommentLine(w, t),
            None: lambda w, t: op.Divide(w, t),
        },
        r_asterisk: {
            r_slash: lambda w, t: Lang.CommentBlock(w, t, open=False),
            None: lambda w, t: op.Multiply(w, t),
        },
        r_comma: lambda w, t: src.lang.base.Comma(w, t),
        r_bang: {
            r_equal: {
                r_equal: {None: lambda w, t: op.UnequalStrict(w, t)},
                None: lambda w, t: op.Unequal(w, t),
            },
            None: lambda w, t: op.Not(w, t),
        },
        r_equal: {
            r_equal: {
                r_equal: {None: lambda w, t: op.EqualStrict(w, t)},
                None: lambda w, t: op.Equal(w, t),
            },
            None: lambda w, t: op.Assign(w, t),
        },
        r_plus: {
            r_plus: lambda w, t: op.Increment(w, t),
            None: lambda w, t: op.Add(w, t),
        },
        r_float: lambda w, t: data.Float(w, t),
        r_int: lambda w, t: data.Integer(w, t),
        r_dash: {
            r_dash: lambda w, t: op.Decrement(w, t),
            r_float: lambda w, t: data.Float(w, t),
            r_int: lambda w, t: data.Integer(w, t),
            None: lambda w, t: op.Subtract(w, t),
        },
        r_greater: lambda w, t: op.Greater(w, t),
        r_lesser: lambda w, t: op.Lesser(w, t),
        r_or: lambda w, t: op.Or(w, t),
        r_nor: lambda w, t: op.Nor(w, t),
        r_xor: lambda w, t: op.Xor(w, t),
        r_and: lambda w, t: op.And(w, t),
        r_nand: lambda w, t: op.Nand(w, t),
        r_not: lambda w, t: op.Not(w, t),
        r_true: lambda w, t: data.Bool(w, t),
        r_false: lambda w, t: data.Bool(w, t),
        r_identifier: lambda w, t: Lang.identifier(w, t),
    }

    keywords = {
        "prnt": lambda w, t: Lang.Prnt(w, t),
        "if": lambda w, t: control.If(w, t),
        "else": lambda w, t: control.Else(w, t),
        "end": lambda w, t: control.End(w, t),
        "for": lambda w, t: control.For(w, t),
        "procedure": lambda w, t: control.Procedure(w, t),
        "def": lambda w, t: control.Def(w, t),
        "exec": lambda w, t: control.Exec(w, t),
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
            OP: lambda: Lang.expression,
            r"<unary-post-op>": lambda: Lang.expression,
            "</delim>|</bracket>": lambda: Lang.expression[r"<const>|<ident>"],
            COMMA: lambda: Lang.expression,
        },
    }

    @staticmethod
    def identifier(w, t):
        if w in Lang.keywords:
            return Lang.keywords[w](w, t)
        elif w in Lang.parameters:
            return Lang.parameters[w](w, t)
        else:
            return Identifier(w, t)

    @staticmethod
    def bind_keyword(keyword, cls):
        Lang.keywords["keyword"] = lambda w, t: cls(w, t)

    class Main(Block):
        @staticmethod
        def type():
            return MAIN

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
            self.condition = parser.build(parser.expression())
            self.until = parser.build(parser.clause(Lang.Until))
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
            self.text = parser.build(parser.expression())
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
            src = parser.expression()
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
                self.legal = self.legal[ll] if not callable(self.legal[ll]) else self.legal[ll]()
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
