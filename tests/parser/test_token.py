from unittest.mock import ANY

import pytest

from src.lang import operator as op
from src.lang.base import (
    Bracket,
)
from src.lang.grammar import Lang
from src.lexer import Token
from src.parser import Parser
from tests.cases import TOKENS, build_test_cases

ANY_POS = (ANY, ANY)


EXPECTED_NEXT = build_test_cases(
    TOKENS,
    [
        [op.Add(Token("+", 0, 0, ANY))],
        [op.Divide(Token("/", 0, 0, ANY))],
        [False],  # :
        [False],  # {
        [False],  # }
        [Bracket(Token("[", 0, 0, ANY))],
        [Bracket(Token("]", 0, 0, ANY))],
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
