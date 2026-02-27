from abc import ABC, abstractmethod

BRACKET_CLOSE = "</bracket>"
BRACKET_OPEN = "<bracket>"
CLAUSE = "<clause>"
COMMA = "<comma>"
CONST = "<const>"
DELIM_CLOSE = "</delim>"
DELIM_OPEN = "<delim>"
DOUBLE_QUOTE = "<d-quote>"
ELSE = "<else>"
END = "<end>"
EXEC = "<exec>"
EXPRESSION = "<parse_expression>"
FOR = "<for>"
IDENT = "<ident>"
IF = "<if>"
INCLUDE = "<include>"
KEYWORD = "<keyword>"
LIST = "<list>"
BLOCK_MAIN = "<main>"
NEWLINE = "<newline>"
OP = "<op>"
PARAMETER = "<parameter>"
PRNT = "<prnt>"
PROCEDURE = "<procedure>"
SINGLE_QUOTE = "<s-quote>"
STRUCT = "<struct>"
UNARY_OP = "<unary-op>"
UNARY_POST_OP = "<unary-post-op>"
WAIT = "<wait>"


class Lexeme(ABC):
    """
    Base class for every language word
    """

    def __init__(self, token, **kwargs):
        self.word = token.word
        self.line = token.line
        self.char = token.char
        self.byte = token.byte
        self.set(kwargs)

    def set(self, kwargs):
        """
        Convenience method for setting properties dynamically
        """
        for i in kwargs:
            setattr(self, i, kwargs[i])

    """
    @staticmethod
    #@abstractmethod
    def type():
        raise NotImplementedError

    #@abstractmethod
    def parse(self, parser, **kwargs):
        pass
    """

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


class Keyword(Lexeme, ABC):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.identifier = None

    def get_identifier(self):
        return self.identifier

    @staticmethod
    def type():
        return KEYWORD

    def __repr__(self):
        return "<keyword %s : %s>" % (self.word, id(self))


class Delimiter(Lexeme, ABC):
    pass


class Identifier(Lexeme):
    @staticmethod
    def type():
        return IDENT

    def eval(self, scope, arguments=None, interp=None):
        v = scope.get(self.word, None)
        if arguments is not None and v is not None:
            return v.call(arguments, interp)
        else:
            return v

    def parse(self, parser, **kwargs):
        raise NotImplementedError


class Parentheses(Delimiter):
    def __init__(self, *args, open: bool = True, **kwargs):
        super().__init__(*args, **kwargs)
        self.open = open

    def type(self):
        return DELIM_OPEN if self.open else DELIM_CLOSE

    def parse(self, parser, **kwargs):
        raise NotImplementedError

    def __repr__(self):
        return DELIM_OPEN if self.open else DELIM_CLOSE


class Bracket(Delimiter):
    def __init__(self, *args, open: bool = True, **kwargs):
        self.open = open
        super().__init__(*args, **kwargs)

    def type(self):
        return BRACKET_OPEN if self.open else BRACKET_CLOSE

    def __repr__(self):
        return BRACKET_OPEN if self.open else BRACKET_CLOSE


class Comma(Delimiter):
    @staticmethod
    def type():
        return COMMA

    def __repr__(self):
        return COMMA


class DoubleQuote(Delimiter):
    @staticmethod
    def type():
        return DOUBLE_QUOTE

    def __repr__(self):
        return DOUBLE_QUOTE


class SingleQuote(Delimiter):
    @staticmethod
    def type():
        return SINGLE_QUOTE

    def __repr__(self):
        return SINGLE_QUOTE


class WhiteSpace(Lexeme):
    pass


class Space(WhiteSpace):
    pass


class NewLine(WhiteSpace):
    @staticmethod
    def type():
        return NEWLINE


class Tab(WhiteSpace):
    pass
