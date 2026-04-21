from src.lang.base import (
    Identifier,
    NewLine,
)
from src.lang.data import Integer
from src.parser import Parser
from src.lang import operator as op
from src.lang.grammar import Lang
from src.lexer import Token
import pytest
from unittest.mock import ANY
from tests.cases import ASSIGNMENT, build_test_cases


ANY_POS = (ANY, ANY)


EXPECTED_NEXT = build_test_cases(
    ASSIGNMENT,
    [
        # ASSIGNMENT
        [
            Identifier(Token("foo", 0, 0, 3)),
            op.Assign(Token("=", 0, 3, 4)),
            Identifier(Token("bar", 0, 4, 7)),
        ],
        [
            Identifier(Token("a", 0, 0, 1)),
            op.Assign(Token("=", 0, 1, 2)),
            Integer(Token("1", 0, 2, 3)),
            NewLine(Token(";", 0, 3, ANY)),
            Identifier(Token("b", 1, 0, 5)),
            op.Assign(Token("=", 1, 1, 6)),
            Integer(Token("2", 1, 2, 7)),
            NewLine(Token(";", 1, 3, ANY)),
            Identifier(Token("a", 2, 0, 9)),
            op.Increment(Token("++", 2, 1, 11)),
            NewLine(Token(";", 2, 3, ANY)),
            Identifier(Token("b", 3, 0, 13)),
            op.Increment(Token("++", 3, 1, 15)),
        ],
        [
            Identifier(Token("a", 0, 0, 1)),
            op.Assign(Token("=", 0, 1, 2)),
            Integer(Token("1", 0, 2, 3)),
            NewLine(Token(";", 0, 3, ANY)),
            Identifier(Token("b", 1, 0, 5)),
            op.Assign(Token("=", 1, 1, 6)),
            Integer(Token("2", 1, 2, 7)),
            NewLine(Token(";", 1, 3, ANY)),
            Identifier(Token("a", 2, 0, 9)),
            op.Decrement(Token("--", 2, 1, 9)),
            NewLine(Token(";", 2, 3, ANY)),
            Identifier(Token("b", 3, 0, 13)),
            op.Decrement(Token("--", 3, 1, 15)),
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
