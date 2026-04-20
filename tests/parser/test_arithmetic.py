from unittest.mock import ANY

import pytest

from src.lang import operator as op
from src.lang.base import (
    Identifier,
    Space,
    Parentheses,
)
from src.lang.data import Integer
from src.lang.grammar import Lang
from src.lexer import Token
from src.parser import Parser
from tests.cases import ARITHMETIC, build_test_cases

ANY_POS = (ANY, ANY)


EXPECTED_NEXT = build_test_cases(
    ARITHMETIC,
    [
        # ARITHMETIC
        [
            Integer(Token("1", 0, 0, 1)),
            op.Add(Token("+", 0, 1, 3)),
            Integer(Token("2", 0, 2, 5)),
        ],
        [
            Integer(Token("1", 0, 0, 1)),
            Space(Token(" ", 0, 1, 2)),
            Space(Token(" ", 0, 2, 3)),
            Space(Token(" ", 0, 3, 4)),
            Space(Token(" ", 0, 4, 5)),
            Space(Token(" ", 0, 5, 6)),
            Space(Token(" ", 0, 6, 7)),
            Space(Token(" ", 0, 7, 8)),
            op.Add(Token("+", 0, 8, 9)),
            Space(Token(" ", 0, 9, 10)),
            Space(Token(" ", 0, 10, 11)),
            Space(Token(" ", 0, 11, 12)),
            Space(Token(" ", 0, 12, 13)),
            Space(Token(" ", 0, 13, 14)),
            Space(Token(" ", 0, 14, 15)),
            Space(Token(" ", 0, 15, 16)),
            Integer(Token("2", 0, 16, 17)),
        ],
        [
            Identifier(Token("a", 0, 0, 1)),
            Space(Token(" ", 0, 1, 2)),
            op.Multiply(Token("*", 0, 2, 3)),
            Space(Token(" ", 0, 3, 4)),
            Identifier(Token("b", 0, 4, 5)),
        ],
        [
            Identifier(Token("a", 0, 0, 1)),
            Space(Token(" ", 0, 1, 2)),
            op.Add(Token("+", 0, 2, 3)),
            Space(Token(" ", 0, 3, 4)),
            Identifier(Token("b", 0, 4, 5)),
            Space(Token(" ", 0, 5, 6)),
            op.Multiply(Token("*", 0, 6, 7)),
            Space(Token(" ", 0, 7, 8)),
            Identifier(Token("c", 0, 8, 9)),
        ],
        [
            Parentheses(Token("(", 0, 0, 1)),
            Identifier(Token("a", 0, 1, 2)),
            Space(Token(" ", 0, 2, 3)),
            op.Add(Token("+", 0, 3, 4)),
            Space(Token(" ", 0, 4, 5)),
            Identifier(Token("b", 0, 5, 6)),
            Parentheses(Token(")", 0, 6, 7)),
            Space(Token(" ", 0, 7, 8)),
            op.Multiply(Token("*", 0, 8, 9)),
            Space(Token(" ", 0, 9, 10)),
            Identifier(Token("c", 0, 10, 11)),
        ],
        [
            Parentheses(Token("(", 0, 0, 1)),
            Integer(Token("1", 0, 1, 2)),
            op.Add(Token("+", 0, 2, 3)),
            Integer(Token("2", 0, 3, 4)),
            Parentheses(Token(")", 0, 4, 5)),
        ],
        [
            Integer(Token("1", 0, 0, 1)),
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
