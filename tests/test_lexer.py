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
        # ("{", [Lang.Bracket("{", ANY_POS, open=True)]),
        # ("{}", [Lang.Bracket("{", ANY_POS, open=True), Lang.Bracket("}", ANY_POS, open=False)]),
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
