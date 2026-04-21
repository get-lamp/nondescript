from unittest.mock import ANY
from src.lexer import Token


def lex(cls, word=None, line=ANY, char=ANY, byte=ANY):
    return cls(Token(word, line, char, byte))
