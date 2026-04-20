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
from tests.cases import COMPARISON, build_test_cases

ANY_POS = (ANY, ANY)


EXPECTED_NEXT = build_test_cases(
    COMPARISON,
    [
        # COMPARISON
        [
            op.UnequalStrict(Token("!==", 0, 0, 3)),
            op.UnequalStrict(Token("!==", 0, 3, 6)),
            op.Unequal(Token("!=", 0, 6, 9)),
            op.UnequalStrict(Token("!==", 0, 8, 9)),
            op.Equal(Token("==", 0, 11, 9)),
        ],
        [
            Identifier(Token("foo", 0, 0, 3)),
            op.Unequal(Token("!=", 0, 3, 5)),
            Identifier(Token("bar", 0, 5, 8)),
        ],
        [
            Identifier(Token("foo", 0, 0, 3)),
            op.UnequalStrict(Token("!==", 0, 3, 6)),
            Identifier(Token("bar", 0, 6, 9)),
        ],
        [
            Integer(Token("1", 0, 0, 1)),
            Space(Token(" ", 0, 1, 2)),
            op.Equal(Token("==", 0, 2, 4)),
            Space(Token(" ", 0, 4, 5)),
            Integer(Token("2", 0, 5, 6)),
        ],
        [
            Integer(Token("1", 0, 0, 1)),
            Space(Token(" ", 0, 1, 2)),
            op.Unequal(Token("!=", 0, 2, 4)),
            Space(Token(" ", 0, 4, 5)),
            Integer(Token("2", 0, 5, 6)),
        ],
        [
            op.UnequalStrict(Token("!==", 0, 0, 3)),
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
