from unittest.mock import ANY

import pytest

from src.lang.base import (
    Identifier,
    Bracket,
)
from src.lang.grammar import Lang
from src.lexer import Token
from src.parser import Parser
from tests.cases import COLLECTIONS, build_test_cases

ANY_POS = (ANY, ANY)


EXPECTED_NEXT = build_test_cases(
    COLLECTIONS,
    [
        [
            Bracket(Token("[", 0, 0, 1)),
            Bracket(Token("]", 0, 1, 2)),
        ],
        [
            Bracket(Token("[", 0, 0, ANY)),
            Identifier(Token("foo", 0, 1, ANY)),
            Bracket(Token("]", 0, 4, ANY)),
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
