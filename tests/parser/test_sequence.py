from unittest.mock import ANY

import pytest

from src.lang import operator as op
from src.lang.base import (
    Identifier,
    NewLine,
)
from src.lang.grammar import Lang
from src.lexer import Token
from src.parser import Parser
from tests.cases import SEQUENCES, build_test_cases

ANY_POS = (ANY, ANY)


EXPECTED_NEXT = build_test_cases(
    SEQUENCES,
    [
        [
            Identifier(Token("foo", 0, 0, ANY)),
            op.Increment(Token("++", 0, 3, ANY)),
            NewLine(Token(";", 0, 5, ANY)),
            Identifier(Token("bar", 1, 0, ANY)),
            op.Increment(Token("++", 1, 3, ANY)),
        ],
        [
            Identifier(Token("foo", 0, 0, ANY)),
            op.Decrement(Token("--", 0, 3, ANY)),
            NewLine(Token(";", 0, 5, ANY)),
            Identifier(Token("bar", 1, 0, ANY)),
            op.Decrement(Token("--", 1, 3, ANY)),
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
