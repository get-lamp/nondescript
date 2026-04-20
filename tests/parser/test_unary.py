from unittest.mock import ANY

import pytest

from src.lang import operator as op
from src.lang.base import (
    Identifier,
    Space,
)
from src.lang.data import Integer
from src.lang.grammar import Lang
from src.lexer import Token
from src.parser import Parser
from tests.cases import UNARY, build_test_cases

ANY_POS = (ANY, ANY)


EXPECTED_NEXT = build_test_cases(
    UNARY,
    [
        # COMPARISON
        [
            Identifier(Token("a", 0, 0, 1)),
            op.Increment(Token("++", 0, 1, 3)),
        ],
        [
            Identifier(Token("a", 0, 0, 1)),
            op.Decrement(Token("--", 0, 1, 3)),
        ],
        [
            op.Not(Token("!", 0, 0, 1)),
            Identifier(Token("a", 0, 1, 2)),
        ],
        [
            op.Not(Token("!", 0, 0, 1)),
            Identifier(Token("foo", 0, 1, 4)),
        ],
        [
            Identifier(Token("foo", 0, 0, 3)),
            op.Increment(Token("++", 0, 3, 5)),
        ],
        [
            Integer(Token("1", 0, 0, 1)),
            op.Add(Token("+", 0, 1, 2)),
            Integer(Token("2", 0, 2, 3)),
            op.Increment(Token("++", 0, 3, 5)),
        ],
        [
            op.Not(Token("NOT", 0, 0, 3)),
            Space(Token(" ", 0, 3, 4)),
            Identifier(Token("bar", 0, 4, 7)),
        ],
    ],
)


@pytest.mark.parametrize(
    ("source", "expected"), EXPECTED_NEXT[:], ids=[src for src, _ in EXPECTED_NEXT[:]]
)
def test_next(source, expected):

    try:
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
    except Exception:
        raise

    assert parser.next() is False
