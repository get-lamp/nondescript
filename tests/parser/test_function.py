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
from src.lang.grammar import Lang, W_DEF, W_END, W_ASSIGN, W_EXEC, W_PROC
from src.parser import Parser
from tests.cases import FUNCTION_DEF, CALLS, PROCEDURES, build_test_cases
from tests.tools import lex

ANY_POS = (ANY, ANY)


EXPECTED_NEXT = build_test_cases(
    FUNCTION_DEF + CALLS + PROCEDURES,
    [
        [
            lex(Def, W_DEF, 0, 0),
            lex(Space, " ", 0, 3),
            lex(Identifier, "func", 0, 4),
            lex(Space, " ", 0, 8),
            lex(Identifier, "a", 0, 9),
            lex(Comma, ",", 0, 10),
            lex(Identifier, "b", 0, 11),
            lex(Comma, ",", 0, 12),
            lex(Identifier, "c", 0, 13),
            lex(NewLine, ";", 0, 14),
            lex(Space, " ", 1, 0),
            lex(End, W_END, 1, 1),
        ],
        [
            lex(Def, W_DEF, 0, 0),
            lex(Space, " ", 0, 3),
            lex(Identifier, "func", 0, 4),
            lex(Space, " ", 0, 8),
            lex(Identifier, "a", 0, 9),
            lex(Comma, ",", 0, 10),
            lex(Identifier, "b", 0, 11),
            lex(Comma, ",", 0, 12),
            lex(Identifier, "c", 0, 13),
            lex(NewLine, "\n", 0, 14),
            lex(End, W_END, 1, 0),
        ],
        [
            lex(Def, W_DEF, 0, 0),
            lex(Space, " ", 0, 3),
            lex(Identifier, "func", 0, 4),
            lex(Space, " ", 0, 8),
            lex(Identifier, "a", 0, 9),
            lex(NewLine, "\n", 0, 10),
            lex(End, W_END, 1, 0),
        ],
        [
            lex(Def, W_DEF, 0, 0),
            lex(Space, " ", 0, 3),
            lex(Identifier, "func", 0, 4),
            lex(NewLine, "\n", 0, 8),
            lex(End, W_END, 1, 0),
        ],
        [
            lex(Def, W_DEF, 0, 0),
            lex(Space, " ", 0, 3),
            lex(Identifier, "func", 0, 4),
            lex(Space, " ", 0, 8),
            lex(Identifier, "a", 0, 9),
            lex(NewLine, "\n", 0, 10),
            lex(Identifier, "x", 1, 0),
            lex(op.Assign, W_ASSIGN, 1, 1),
            lex(Integer, "0", 1, 2),
            lex(NewLine, "\n", 1, 3),
            lex(End, W_END, 2, 0),
        ],
        [
            lex(Def, W_DEF, 0, 0),
            lex(Space, " ", 0, 3),
            lex(Identifier, "func", 0, 4),
            lex(Space, " ", 0, 8),
            lex(Identifier, "a", 0, 9),
            lex(Comma, ",", 0, 10),
            lex(Identifier, "b", 0, 11),
            lex(Comma, ",", 0, 12),
            lex(Identifier, "c", 0, 13),
            lex(NewLine, "\n", 0, 14),
            lex(Identifier, "x", 1, 0),
            lex(op.Assign, W_ASSIGN, 1, 1),
            lex(Integer, "0", 1, 2),
            lex(NewLine, "\n", 1, 3),
            lex(End, W_END, 2, 0),
        ],
        [
            lex(Def, W_DEF, 0, 0),
            lex(Space, " ", 0, 3),
            lex(Identifier, "func", 0, 4),
            lex(NewLine, "\n", 0, 8),
            lex(Identifier, "x", 1, 0),
            lex(op.Assign, W_ASSIGN, 1, 1),
            lex(Integer, "0", 1, 2),
            lex(NewLine, ";", 1, 3),
            lex(Identifier, "y", 2, 0),
            lex(op.Assign, W_ASSIGN, 2, 1),
            lex(Integer, "1", 2, 2),
            lex(NewLine, ";", 2, 3),
            lex(Identifier, "z", 3, 0),
            lex(op.Assign, W_ASSIGN, 3, 1),
            lex(Integer, "2", 3, 2),
            lex(NewLine, "\n", 3, 3),
            lex(End, W_END, 4, 0),
        ],
        # CALLS
        [
            lex(Exec, W_EXEC, 0, 0, 4),
            lex(Space, " ", 0, 4, 5),
            lex(Identifier, "my_proc", 0, 5, 12),
        ],
        # PROCEDURES
        [
            lex(Procedure, W_PROC, 0, 0, 9),
            lex(Space, " ", 0, 9, 10),
            lex(Identifier, "my_proc", 0, 10, 17),
        ],
    ],
)


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


EXPECTED_PARSE_BLOCKS = [
    (
        "def f a\na\nend",
        [lex(Def, W_DEF), [lex(Identifier, "f")], [lex(Identifier, "a")]],
    ),
    (
        "def func a,b,c; end",
        [
            lex(Def, W_DEF),
            [lex(Identifier, "func")],
            [[lex(Identifier, "a")], [lex(Identifier, "b")], [lex(Identifier, "c")]],
        ],
    ),
]


@pytest.mark.parametrize(
    ("source", "expected"),
    EXPECTED_PARSE_BLOCKS[1:],
    ids=[src for src, _ in EXPECTED_PARSE_BLOCKS[1:0]],
)
def test_end_pulls_block(source, expected):
    parser = Parser(Lang, source)
    assert parser.parse() == expected
    assert parser.parse() is False


EXPECTED_PARSE = build_test_cases(
    FUNCTION_DEF[0:1],
    [
        [
            lex(Def, W_DEF),
            [lex(Identifier, "func")],
            [[lex(Identifier, "a")], [lex(Identifier, "b")], [lex(Identifier, "c")]],
        ]
    ],
)


@pytest.mark.parametrize(
    ("source", "expected"), EXPECTED_PARSE[:], ids=[src for src, _ in EXPECTED_PARSE[:]]
)
def test_parse(source, expected):

    assert Parser(Lang, source).parse() == expected
