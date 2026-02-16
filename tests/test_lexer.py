from src.lexer import Lexer
from src.lang import Lang
import pytest
from unittest.mock import ANY

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
        ("foo=bar", [Lang.Identifier("foo", (0, 0)), Lang.Assign("=", (0, 3)), Lang.Identifier("bar", (0, 4))]),
        ("foo=123", [Lang.Identifier("foo", (0, 0)), Lang.Assign("=", (0, 3)), Lang.Integer("123", (0, 4))]),
        (
            'foo="abc"',
            [
                Lang.Identifier("foo", (0, 0)),
                Lang.Assign("=", (0, 3)),
                Lang.DoubleQuote('"', (0, 4)),
                Lang.Identifier("abc", (0, 5)),
                Lang.DoubleQuote('"', (0, 8)),
            ],
        ),
        (
            "foo[0]",
            [
                Lang.Identifier("foo", (0, 0)),
                Lang.Bracket("[", (0, 3)),
                Lang.Integer("0", (0, 4)),
                Lang.Bracket("]", (0, 5)),
            ],
        ),
        ("!foo", [Lang.UnaryOperator("!", (0, 0)), Lang.Identifier("foo", (0, 1))]),
        ("NOT", [Lang.Not("NOT", (0, 0))]),
        ("prnt 123", [Lang.Prnt("prnt", (0, 0)), Lang.Space(" ", (0, 4)), Lang.Integer("123", (0, 5))]),
        ("   ", [Lang.Space(" ", (0, 0)), Lang.Space(" ", (0, 1)), Lang.Space(" ", (0, 2))]),
        ("a=", [Lang.Identifier("a", (0, 0)), Lang.Assign("=", (0, 1))]),
        ("==", [Lang.Equal("==", (0, 0))]),
        ("===", [Lang.EqualStrict("===", (0, 0))]),
        ("!", [Lang.UnaryOperator("!", (0, 0))]),
        ("!=", [Lang.Inequal("!=", (0, 0))]),
        ("!==", [Lang.InequalStrict("!==", (0, 0))]),
        ("[", [Lang.Bracket("[", (0, 0))]),
        ("[[", [Lang.Bracket("[", (0, 0)), Lang.Bracket("[", (0, 1))]),
        ("]", [Lang.Bracket("]", (0, 0))]),
        ("]]", [Lang.Bracket("]", (0, 0)), Lang.Bracket("]", (0, 1))]),
        ("[]", [Lang.Bracket("[", (0, 0)), Lang.Bracket("]", (0, 1))]),
        (
            "[[]]",
            [
                Lang.Bracket("[", (0, 0)),
                Lang.Bracket("[", (0, 1)),
                Lang.Bracket("]", (0, 2)),
                Lang.Bracket("]", (0, 3)),
            ],
        ),
        (
            "1.23",
            [Lang.Float("1.23", (0, 0))],
        ),
        (
            "// This is a comment",
            [
                Lang.CommentLine("//", (0, 0)),
                Lang.Space(" ", (0, 2)),
                Lang.Identifier("This", (0, 3)),
                Lang.Space(" ", (0, 7)),
                Lang.Identifier("is", (0, 8)),
                Lang.Space(" ", (0, 10)),
                Lang.Identifier("a", (0, 11)),
                Lang.Space(" ", (0, 12)),
                Lang.Identifier("comment", (0, 13)),
            ],
        ),
        (
            "/* Block comment */",
            [
                Lang.CommentBlock("/*", (0, 0), open=True),
                Lang.Space(" ", (0, 2)),
                Lang.Identifier("Block", (0, 3)),
                Lang.Space(" ", (0, 8)),
                Lang.Identifier("comment", (0, 9)),
                Lang.Space(" ", (0, 16)),
                Lang.CommentBlock("*/", (0, 17), open=False),
            ],
        ),
        (
            "1+2-3*4/5",
            [
                Lang.Integer("1", (0, 0)),
                Lang.Add("+", (0, 1)),
                Lang.Integer("2", (0, 2)),
                Lang.Integer("-3", (0, 3)),
                Lang.Multiply("*", (0, 5)),
                Lang.Integer("4", (0, 6)),
                Lang.Divide("/", (0, 7)),
                Lang.Integer("5", (0, 8)),
            ],
        ),
        (
            "++foo",
            [Lang.Increment("++", (0, 0)), Lang.Identifier("foo", (0, 2))],
        ),
        (
            "--bar",
            [Lang.Decrement("--", (0, 0)), Lang.Identifier("bar", (0, 2))],
        ),
        (
            "(a + b)",
            [
                Lang.Parentheses("(", (0, 0), open=True),
                Lang.Identifier("a", (0, 1)),
                Lang.Space(" ", (0, 2)),
                Lang.Add("+", (0, 3)),
                Lang.Space(" ", (0, 4)),
                Lang.Identifier("b", (0, 5)),
                Lang.Parentheses(")", (0, 6), open=False),
            ],
        ),
        (
            "if 1==1 then prnt 'true' end",
            [
                Lang.If("if", (0, 0)),
                Lang.Space(" ", (0, 2)),
                Lang.Integer("1", (0, 3)),
                Lang.Equal("==", (0, 4)),
                Lang.Integer("1", (0, 6)),
                Lang.Space(" ", (0, 7)),
                Lang.Identifier("then", (0, 8)),
                Lang.Space(" ", (0, 12)),
                Lang.Prnt("prnt", (0, 13)),
                Lang.Space(" ", (0, 17)),
                Lang.SingleQuote("'", (0, 18)),
                Lang.Identifier("true", (0, 19)),
                Lang.SingleQuote("'", (0, 23)),
                Lang.Space(" ", (0, 24)),
                Lang.End("end", (0, 25)),
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
