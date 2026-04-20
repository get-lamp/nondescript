from unittest.mock import ANY

import pytest

from src.lang import operator as op
from src.lang.base import (
    Identifier,
    Space,
    SingleQuote,
)
from src.lang.grammar import Lang
from src.lexer import Token
from src.parser import Parser
from tests.cases import LITERALS, build_test_cases

ANY_POS = (ANY, ANY)


EXPECTED_NEXT = build_test_cases(
    LITERALS,
    [
        [
            Lang.Prnt(Token("prnt", 0, 0, 4)),
            Space(Token(" ", 0, 4, 5)),
            SingleQuote(Token("'", 0, 5, 6)),
            Identifier(Token("hello", 0, 6, 11)),
            SingleQuote(Token("'", 0, 11, 12)),
        ],
        [
            SingleQuote(Token("'", 0, 0, 1)),
            Identifier(Token("Hello", 0, 1, 6)),
            SingleQuote(Token("'", 0, 6, 7)),
            Space(Token(" ", 0, 7, 8)),
            op.Add(Token("+", 0, 8, 9)),
            Space(Token(" ", 0, 9, 10)),
            SingleQuote(Token("'", 0, 10, 11)),
            Space(Token(" ", 0, 11, 12)),
            SingleQuote(Token("'", 0, 12, 13)),
            Space(Token(" ", 0, 13, 14)),
            op.Add(Token("+", 0, 14, 15)),
            Space(Token(" ", 0, 15, 16)),
            Identifier(Token("who", 0, 16, 19)),
        ],
        [
            Identifier(Token("foo", 0, 0, 3)),
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
