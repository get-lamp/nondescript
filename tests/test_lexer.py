from unittest.mock import ANY

import pytest

import src.lang.base
from src.lang import operator as op
from src.lang.base import Identifier, Bracket, DoubleQuote
from src.lang.data import Integer, Bool, Float
from src.lang.flow import If, End
from src.lang.grammar import Lang
from src.lexer import Lexer

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
                Lexer.Token("foo", 0, 0),
                Lexer.Token(";", 0, 3),
                Lexer.Token("bar", 1, 0),
                Lexer.Token(";", 1, 3),
                Lexer.Token("baz", 2, 0),
            ],
        ),
        (
            "foo\nbar\nbaz",
            [
                Lexer.Token("foo", 0, 0),
                Lexer.Token("\n", 0, 3),
                Lexer.Token("bar", 1, 0),
                Lexer.Token("\n", 1, 3),
                Lexer.Token("baz", 2, 0),
            ],
        ),
        (
            "foo bar baz",
            [
                Lexer.Token("foo", 0, 0),
                Lexer.Token(" ", 0, 3),
                Lexer.Token("bar", 0, 4),
                Lexer.Token(" ", 0, 7),
                Lexer.Token("baz", 0, 8),
            ],
        ),
        (
            "# ^ &",
            [
                Lexer.Token("#", 0, 0),
                Lexer.Token(" ", 0, 1),
                Lexer.Token("^", 0, 2),
                Lexer.Token(" ", 0, 3),
                Lexer.Token("&", 0, 4),
            ],
        ),
        (
            "0\n1\n2",
            [
                Lexer.Token("0", 0, 0),
                Lexer.Token("\n", 0, 1),
                Lexer.Token("1", 1, 0),
                Lexer.Token("\n", 1, 1),
                Lexer.Token("2", 2, 0),
            ],
        ),
        (
            "foo=bar",
            [
                Lexer.Token("foo", 0, 0),
                Lexer.Token("=", 0, 3),
                Lexer.Token("bar", 0, 4),
            ],
        ),
    ],
)
def test_scan_keeps_track_of_char_and_line_number(source, expected):

    lexer = Lexer(Lang, source)

    for exp in expected:
        token = lexer._scan()
        assert token == exp
        assert type(token) is type(exp)

    assert lexer._scan() is None


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        ("foo=bar", [Identifier("foo", (0, 0)), op.Assign("=", (0, 3)), Identifier("bar", (0, 4))]),
        ("foo=123", [Identifier("foo", (0, 0)), op.Assign("=", (0, 3)), Integer("123", (0, 4))]),
        (
            'foo="abc"',
            [
                Identifier("foo", (0, 0)),
                op.Assign("=", (0, 3)),
                DoubleQuote('"', (0, 4)),
                Identifier("abc", (0, 5)),
                DoubleQuote('"', (0, 8)),
            ],
        ),
        (
            "foo[0]",
            [
                Identifier("foo", (0, 0)),
                Bracket("[", (0, 3)),
                Integer("0", (0, 4)),
                src.lang.base.Bracket("]", (0, 5)),
            ],
        ),
        ("!foo", [op.Not("!", (0, 0)), Identifier("foo", (0, 1))]),
        ("NOT", [op.Not("NOT", (0, 0))]),
        ("prnt 123", [Lang.Prnt("prnt", (0, 0)), src.lang.base.Space(" ", (0, 4)), Integer("123", (0, 5))]),
        ("   ", [src.lang.base.Space(" ", (0, 0)), src.lang.base.Space(" ", (0, 1)), src.lang.base.Space(" ", (0, 2))]),
        ("a=", [Identifier("a", (0, 0)), op.Assign("=", (0, 1))]),
        ("--", [op.Decrement("--", (0, 0))]),
        ("----", [op.Decrement("--", (0, 0)), op.Decrement("--", (0, 2))]),
        ("--++", [op.Decrement("--", (0, 0)), op.Increment("++", (0, 2))]),
        ("++++", [op.Increment("++", (0, 0)), op.Increment("++", (0, 2))]),
        ("++--", [op.Increment("++", (0, 0)), op.Decrement("--", (0, 2))]),
        ("==", [op.Equal("==", (0, 0))]),
        ("===", [op.EqualStrict("===", (0, 0))]),
        ("!", [op.Not("!", (0, 0))]),
        ("!=", [op.Unequal("!=", (0, 0))]),
        ("!==", [op.UnequalStrict("!==", (0, 0))]),
        ("[", [src.lang.base.Bracket("[", (0, 0))]),
        ("[[", [src.lang.base.Bracket("[", (0, 0)), src.lang.base.Bracket("[", (0, 1))]),
        ("]", [src.lang.base.Bracket("]", (0, 0))]),
        ("]]", [src.lang.base.Bracket("]", (0, 0)), src.lang.base.Bracket("]", (0, 1))]),
        ("[]", [src.lang.base.Bracket("[", (0, 0)), src.lang.base.Bracket("]", (0, 1))]),
        (
            "[[]]",
            [
                src.lang.base.Bracket("[", (0, 0)),
                src.lang.base.Bracket("[", (0, 1)),
                src.lang.base.Bracket("]", (0, 2)),
                src.lang.base.Bracket("]", (0, 3)),
            ],
        ),
        (
            "1.23",
            [Float("1.23", (0, 0))],
        ),
        (
            "// This is a comment",
            [
                Lang.CommentLine("//", (0, 0)),
                src.lang.base.Space(" ", (0, 2)),
                Identifier("This", (0, 3)),
                src.lang.base.Space(" ", (0, 7)),
                Identifier("is", (0, 8)),
                src.lang.base.Space(" ", (0, 10)),
                Identifier("a", (0, 11)),
                src.lang.base.Space(" ", (0, 12)),
                Identifier("comment", (0, 13)),
            ],
        ),
        (
            "/* Block comment */",
            [
                Lang.CommentBlock("/*", (0, 0), open=True),
                src.lang.base.Space(" ", (0, 2)),
                Identifier("Block", (0, 3)),
                src.lang.base.Space(" ", (0, 8)),
                Identifier("comment", (0, 9)),
                src.lang.base.Space(" ", (0, 16)),
                Lang.CommentBlock("*/", (0, 17), open=False),
            ],
        ),
        (
            "1+2-3*4/5",
            [
                Integer("1", (0, 0)),
                op.Add("+", (0, 1)),
                Integer("2", (0, 2)),
                Integer("-3", (0, 3)),
                op.Multiply("*", (0, 5)),
                Integer("4", (0, 6)),
                op.Divide("/", (0, 7)),
                Integer("5", (0, 8)),
            ],
        ),
        (
            "++foo",
            [op.Increment("++", (0, 0)), Identifier("foo", (0, 2))],
        ),
        (
            "foo++",
            [Identifier("foo", (0, 0)), op.Increment("++", (0, 3))],
        ),
        (
            "(a + b)",
            [
                src.lang.base.Parentheses("(", (0, 0), open=True),
                Identifier("a", (0, 1)),
                src.lang.base.Space(" ", (0, 2)),
                op.Add("+", (0, 3)),
                src.lang.base.Space(" ", (0, 4)),
                Identifier("b", (0, 5)),
                src.lang.base.Parentheses(")", (0, 6), open=False),
            ],
        ),
        (
            "if 1==1 then prnt 'true' end",
            [
                If("if", (0, 0)),
                src.lang.base.Space(" ", (0, 2)),
                Integer("1", (0, 3)),
                op.Equal("==", (0, 4)),
                Integer("1", (0, 6)),
                src.lang.base.Space(" ", (0, 7)),
                Identifier("then", (0, 8)),
                src.lang.base.Space(" ", (0, 12)),
                Lang.Prnt("prnt", (0, 13)),
                src.lang.base.Space(" ", (0, 17)),
                src.lang.base.SingleQuote("'", (0, 18)),
                Bool("true", (0, 19)),
                src.lang.base.SingleQuote("'", (0, 23)),
                src.lang.base.Space(" ", (0, 24)),
                End("end", (0, 25)),
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
        assert token == exp
        assert type(token) is type(exp)

    # assert it ends when we expect it
    assert lexer.next() is False


@pytest.mark.parametrize("source", ("{", "}"))
def test_next_is_false(source):
    lexer = Lexer(Lang, source)

    assert lexer.next() is False
