from unittest.mock import ANY

import pytest

from src.lang import operator as op
from src.lang.base import (
    Identifier,
    Space,
    NewLine,
    Comma,
)
from src.lang.control import Procedure, Exec, Def, End
from src.lang.data import Integer
from src.lang.grammar import (
    Lang,
    W_DEF,
    W_SPACE,
    W_END
)
from src.lexer import Token
from src.parser import Parser
from tests.cases import FUNCTION_DEF, CALLS, PROCEDURES, build_test_cases

ANY_POS = (ANY, ANY)


def _lex(cls, word=None, line=ANY, char=ANY, byte=ANY):
    return cls(Token(word, line, char, byte))


EXPECTED_NEXT = build_test_cases(
    FUNCTION_DEF + CALLS + PROCEDURES,
    [
        [
            _lex(Def, W_DEF, 0, 0),
            _lex(Space, W_SPACE, 0, 3),
            _lex(Identifier, 'func', 0, 4),
            _lex(Space, W_SPACE, 0, 8),
            _lex(Identifier, 'a', 0, 9),
            _lex(Comma, ',', 0, 10),
            _lex(Identifier, 'b', 0, 11),
            _lex(Comma, ',', 0, 12),
            _lex(Identifier, 'c', 0, 13),
            # ignoring delimiter ':'
            _lex(Space, W_SPACE, 0, 15),
            _lex(End, W_END, 0, 16),
        ],
        [
            Def(Token("def", 0, 0, ANY)),
            Space(Token(" ", 0, 3, ANY)),
            Identifier(Token("func", 0, 4, ANY)),
            Space(Token(" ", 0, 8, ANY)),
            Identifier(Token("a", 0, 9, ANY)),
            Comma(Token(",", 0, 10, ANY)),
            Identifier(Token("b", 0, 11, ANY)),
            Comma(Token(",", 0, 12, ANY)),
            Identifier(Token("c", 0, 13, ANY)),
            NewLine(Token("\n", 0, 14, ANY)),
            End(Token("end", 1, 0, ANY)),
        ],
        [
            Def(Token("def", 0, 0, ANY)),
            Space(Token(" ", 0, 3, ANY)),
            Identifier(Token("func", 0, 4, ANY)),
            Space(Token(" ", 0, 8, ANY)),
            Identifier(Token("a", 0, 9, ANY)),
            NewLine(Token("\n", 0, 10, ANY)),
            End(Token("end", 1, 0, ANY)),
        ],
        [
            Def(Token("def", 0, 0, ANY)),
            Space(Token(" ", 0, 3, ANY)),
            Identifier(Token("func", 0, 4, ANY)),
            NewLine(Token("\n", 0, ANY, ANY)),
            End(Token("end", 1, 0, ANY)),
        ],
        [
            Def(Token("def", 0, 0, ANY)),
            Space(Token(" ", 0, 3, ANY)),
            Identifier(Token("func", 0, 4, ANY)),
            Space(Token(" ", 0, 8, ANY)),
            Identifier(Token("a", 0, 9, ANY)),
            NewLine(Token("\n", 0, ANY, ANY)),
            Identifier(Token("x", 1, 0, ANY)),
            op.Assign(Token("=", 1, 1, ANY)),
            Integer(Token("0", 1, 2, ANY)),
            NewLine(Token("\n", 1, ANY, ANY)),
            End(Token("end", 2, 0, ANY)),
        ],
        [
            Def(Token("def", 0, 0, ANY)),
            Space(Token(" ", 0, 3, ANY)),
            Identifier(Token("func", 0, 4, ANY)),
            Space(Token(" ", 0, 8, ANY)),
            Identifier(Token("a", 0, 9, ANY)),
            Comma(Token(",", 0, 10, ANY)),
            Identifier(Token("b", 0, 11, ANY)),
            Comma(Token(",", 0, 12, ANY)),
            Identifier(Token("c", 0, 13, ANY)),
            NewLine(Token("\n", 0, ANY, ANY)),
            Identifier(Token("x", 1, 0, ANY)),
            op.Assign(Token("=", 1, 1, ANY)),
            Integer(Token("0", 1, 2, ANY)),
            NewLine(Token("\n", 1, ANY, ANY)),
            End(Token("end", 2, 0, ANY)),
        ],
        [
            Def(Token("def", 0, 0, ANY)),
            Space(Token(" ", 0, 3, ANY)),
            Identifier(Token("func", 0, 4, ANY)),
            NewLine(Token("\n", 0, ANY, ANY)),
            Identifier(Token("x", 1, 0, ANY)),
            op.Assign(Token("=", 1, 1, ANY)),
            Integer(Token("0", 1, 2, ANY)),
            NewLine(Token(";", 1, 3, ANY)),
            Identifier(Token("y", 2, 0, ANY)),
            op.Assign(Token("=", 2, 1, ANY)),
            Integer(Token("1", 2, 2, ANY)),
            NewLine(Token(";", 2, 3, ANY)),
            Identifier(Token("z", 3, 0, ANY)),
            op.Assign(Token("=", 3, 1, ANY)),
            Integer(Token("2", 3, 2, ANY)),
            NewLine(Token("\n", 3, 3, ANY)),
            End(Token("end", 4, 0, ANY)),
        ],
        # CALLS
        [
            Exec(Token("exec", 0, 0, 4)),
            Space(Token(" ", 0, 4, 5)),
            Identifier(Token("my_proc", 0, 5, 12)),
        ],
        # PROCEDURES
        [
            Procedure(Token("procedure", 0, 0, 9)),
            Space(Token(" ", 0, 9, 10)),
            Identifier(Token("my_proc", 0, 10, 17)),
        ],
    ],
)

"""
EXPECTED_PARSE = build_test_cases(
    FUNCTION_DEF,
    [
        [Def(Token("def", ANY, ANY, ANY)),[]]
    ]
)
"""

@pytest.mark.parametrize(
    ("source", "expected"), EXPECTED_NEXT[:], ids=[src for src, _ in EXPECTED_NEXT[:]]
)
def test_next(source, expected):

    parser = Parser(Lang, source)

    for exp in expected:
        token = parser.lexer.next()

        if isinstance(exp, bool):
            assert token == exp
            break

        assert token.word == exp.word
        assert token.char == exp.char
        assert token.line == exp.line
        assert type(token) is type(exp)

    assert parser.next() is False

"""
@pytest.mark.parametrize(
    ("source", "expected"), EXPECTED_PARSE[:], ids=[src for src, _ in EXPECTED_PARSE[:]]
)
def test_parse(source, expected):
    assert Parser(Lang, source).parse() == expected

"""