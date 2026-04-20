from src.lang.base import (
    Identifier,
    Space,
)
from unittest.mock import ANY

import pytest

from src.lang import operator as op
from src.lang.control import If
from src.lang.data import Bool
from src.lang.grammar import Lang
from src.lexer import Token
from src.parser import Parser
from tests.cases import CONTROL_FLOW, build_test_cases

ANY_POS = (ANY, ANY)


EXPECTED_NEXT = build_test_cases(
    CONTROL_FLOW,
    [
        # COMPARISON
        [
            If(Token("if", 0, 0, 2)),
            Space(Token(" ", 0, 2, 3)),
            Identifier(Token("foo", 0, 3, 6)),
            op.Equal(Token("==", 0, 6, 8)),
            Identifier(Token("bar", 0, 8, 11)),
        ],
        [
            If(Token("if", 0, 0, 2)),
            Space(Token(" ", 0, 2, 3)),
            Bool(Token("TRUE", 0, 3, 7)),
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
