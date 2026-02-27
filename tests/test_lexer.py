from unittest.mock import ANY

import pytest

from src.lang import operator as op
from src.lang.base import (
    Identifier,
    Bracket,
    DoubleQuote,
    Space,
    Parentheses,
    SingleQuote,
)
from src.lang.data import Integer, Bool, Float
from src.lang.control import If, End
from src.lang.grammar import Lang
from src.lexer import Lexer, Token

ANY_POS = (ANY, ANY)


@pytest.mark.parametrize("char", ["\n", ";"])
def test_is_newline(char):
    lexer = Lexer(Lang, None)
    assert lexer._is_newline(char) is True


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        (
            "foo;bar;baz",
            [
                Token("foo", 0, 0, 0),
                Token(";", 0, 3, 3),
                Token("bar", 1, 0, 4),
                Token(";", 1, 3, 7),
                Token("baz", 2, 0, 8),
            ],
        ),
        (
            "foo\nbar\nbaz",
            [
                Token("foo", 0, 0, 0),
                Token("\n", 0, 3, 3),
                Token("bar", 1, 0, 4),
                Token("\n", 1, 3, 7),
                Token("baz", 2, 0, 8),
            ],
        ),
        (
            "foo bar baz",
            [
                Token("foo", 0, 0, 0),
                Token(" ", 0, 3, 3),
                Token("bar", 0, 4, 4),
                Token(" ", 0, 7, 7),
                Token("baz", 0, 8, 8),
            ],
        ),
        (
            "# ^ &",
            [
                Token("#", 0, 0, 0),
                Token(" ", 0, 1, 1),
                Token("^", 0, 2, 2),
                Token(" ", 0, 3, 3),
                Token("&", 0, 4, 4),
            ],
        ),
        (
            "0\n1\n2",
            [
                Token("0", 0, 0, 0),
                Token("\n", 0, 1, 1),
                Token("1", 1, 0, 2),
                Token("\n", 1, 1, 3),
                Token("2", 2, 0, 4),
            ],
        ),
        (
            "foo=bar",
            [
                Token("foo", 0, 0, 0),
                Token("=", 0, 3, 3),
                Token("bar", 0, 4, 4),
            ],
        ),
    ],
)
def test_scan_keeps_track_of_char_line_number_and_byte(source, expected):

    lexer = Lexer(Lang, source)

    for exp in expected:
        token = lexer._scan()
        assert token.char == exp.char
        assert token.line == exp.line
        assert token.word == exp.word
        assert token.byte == exp.byte
        assert token == exp
        assert type(token) is type(exp)

    assert lexer._scan() is None


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        (
            "foo=bar",
            [
                Identifier(Token("foo", 0, 0, 0)),
                op.Assign(Token("=", 0, 3, 3)),
                Identifier(Token("bar", 0, 4, 4)),
            ],
        ),
        (
            "foo=123",
            [
                Identifier(Token("foo", 0, 0, 0)),
                op.Assign(Token("=", 0, 3, 3)),
                Integer(Token("123", 0, 4, 4)),
            ],
        ),
        (
            'foo="abc"',
            [
                Identifier(Token("foo", 0, 0, 0)),
                op.Assign(Token("=", 0, 3, 3)),
                DoubleQuote(Token('"', 0, 4, 4)),
                Identifier(Token("abc", 0, 5, 5)),
                DoubleQuote(Token('"', 0, 8, 8)),
            ],
        ),
        (
            "foo[0]",
            [
                Identifier(Token("foo", 0, 0, 0)),
                Bracket(Token("[", 0, 3, 3)),
                Integer(Token("0", 0, 4, 4)),
                Bracket(Token("]", 0, 5, 5)),
            ],
        ),
        ("!foo", [op.Not(Token("!", 0, 0, 0)), Identifier(Token("foo", 0, 1, 1))]),
        ("NOT", [op.Not(Token("NOT", 0, 0, 0))]),
        (
            "prnt 123",
            [
                Lang.Prnt(Token("prnt", 0, 0, 0)),
                Space(Token(" ", 0, 4, 4)),
                Integer(Token("123", 0, 5, 5)),
            ],
        ),
        (
            "   ",
            [
                Space(Token(" ", 0, 0, 0)),
                Space(Token(" ", 0, 1, 1)),
                Space(Token(" ", 0, 2, 2)),
            ],
        ),
        ("a=", [Identifier(Token("a", 0, 0, 0)), op.Assign(Token("=", 0, 1, 1))]),
        ("--", [op.Decrement(Token("--", 0, 0, 0))]),
        (
            "----",
            [op.Decrement(Token("--", 0, 0, 0)), op.Decrement(Token("--", 0, 2, 2))],
        ),
        (
            "--++",
            [op.Decrement(Token("--", 0, 0, 0)), op.Increment(Token("++", 0, 2, 2))],
        ),
        (
            "++++",
            [op.Increment(Token("++", 0, 0, 0)), op.Increment(Token("++", 0, 2, 2))],
        ),
        (
            "++--",
            [op.Increment(Token("++", 0, 0, 0)), op.Decrement(Token("--", 0, 2, 2))],
        ),
        ("==", [op.Equal(Token("==", 0, 0, 0))]),
        ("===", [op.EqualStrict(Token("===", 0, 0, 0))]),
        ("!", [op.Not(Token("!", 0, 0, 0))]),
        ("!=", [op.Unequal(Token("!=", 0, 0, 0))]),
        ("!==", [op.UnequalStrict(Token("!==", 0, 0, 0))]),
        ("[", [Bracket(Token("[", 0, 0, 0))]),
        ("[[", [Bracket(Token("[", 0, 0, 0)), Bracket(Token("[", 0, 1, 1))]),
        ("]", [Bracket(Token("]", 0, 0, 0))]),
        ("]]", [Bracket(Token("]", 0, 0, 0)), Bracket(Token("]", 0, 1, 1))]),
        ("[]", [Bracket(Token("[", 0, 0, 0)), Bracket(Token("]", 0, 1, 1))]),
        (
            "[[]]",
            [
                Bracket(Token("[", 0, 0, 0)),
                Bracket(Token("[", 0, 1, 1)),
                Bracket(Token("]", 0, 2, 2)),
                Bracket(Token("]", 0, 3, 3)),
            ],
        ),
        (
            "1.23",
            [Float(Token("1.23", 0, 0, 0))],
        ),
        (
            "// This is a comment",
            [
                Lang.CommentLine(Token("//", 0, 0, 0)),
                Space(Token(" ", 0, 2, 2)),
                Identifier(Token("This", 0, 3, 3)),
                Space(Token(" ", 0, 7, 7)),
                Identifier(Token("is", 0, 8, 8)),
                Space(Token(" ", 0, 10, 10)),
                Identifier(Token("a", 0, 11, 11)),
                Space(Token(" ", 0, 12, 12)),
                Identifier(Token("comment", 0, 13, 13)),
            ],
        ),
        (
            "/* Block comment */",
            [
                Lang.CommentBlock(Token("/*", 0, 0, 0), open=True),
                Space(Token(" ", 0, 2, 2)),
                Identifier(Token("Block", 0, 3, 3)),
                Space(Token(" ", 0, 8, 8)),
                Identifier(Token("comment", 0, 9, 9)),
                Space(Token(" ", 0, 16, 16)),
                Lang.CommentBlock(Token("*/", 0, 17, 17), open=False),
            ],
        ),
        (
            "1+2-3*4/5",
            [
                Integer(Token("1", 0, 0, 0)),
                op.Add(Token("+", 0, 1, 1)),
                Integer(Token("2", 0, 2, 2)),
                Integer(Token("-3", 0, 3, 3)),
                op.Multiply(Token("*", 0, 5, 5)),
                Integer(Token("4", 0, 6, 6)),
                op.Divide(Token("/", 0, 7, 7)),
                Integer(Token("5", 0, 8, 8)),
            ],
        ),
        (
            "++foo",
            [op.Increment(Token("++", 0, 0, 0)), Identifier(Token("foo", 0, 2, 2))],
        ),
        (
            "foo++",
            [Identifier(Token("foo", 0, 0, 0)), op.Increment(Token("++", 0, 3, 3))],
        ),
        (
            "(a + b)",
            [
                Parentheses(Token("(", 0, 0, 0), open=True),
                Identifier(Token("a", 0, 1, 1)),
                Space(Token(" ", 0, 2, 2)),
                op.Add(Token("+", 0, 3, 3)),
                Space(Token(" ", 0, 4, 4)),
                Identifier(Token("b", 0, 5, 5)),
                Parentheses(Token(")", 0, 6, 6), open=False),
            ],
        ),
        (
            "if 1==1 then prnt 'true' end",
            [
                If(Token("if", 0, 0, 0)),
                Space(Token(" ", 0, 2, 2)),
                Integer(Token("1", 0, 3, 3)),
                op.Equal(Token("==", 0, 4, 4)),
                Integer(Token("1", 0, 6, 6)),
                Space(Token(" ", 0, 7, 7)),
                Identifier(Token("then", 0, 8, 8)),
                Space(Token(" ", 0, 12, 12)),
                Lang.Prnt(Token("prnt", 0, 13, 13)),
                Space(Token(" ", 0, 17, 17)),
                SingleQuote(Token("'", 0, 18, 18)),
                Bool(Token("true", 0, 19, 19)),
                SingleQuote(Token("'", 0, 23, 23)),
                Space(Token(" ", 0, 24, 24)),
                End(Token("end", 0, 25, 25)),
            ],
        ),
    ],
)
def test_next(source, expected):
    lexer = Lexer(Lang, source)

    for exp in expected:
        token = lexer.next()
        assert token.word == exp.word
        assert token.line == exp.line
        assert token.char == exp.char
        assert token.byte == exp.byte
        assert token == exp
        assert type(token) is type(exp)

    # assert it ends when we expect it
    assert lexer.next() is False


@pytest.mark.parametrize("source", ("{", "}"))
def test_next_is_false(source):
    lexer = Lexer(Lang, source)

    assert lexer.next() is False
