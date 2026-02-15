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


def test_scan_at_end_of_source():
    lexer = Lexer(Lang, "foo=bar")
    assert (lexer._scan()).word == "foo"
    assert (lexer._scan()).word == "="
    assert (lexer._scan()).word == "bar"
    assert lexer._scan() is None


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        ("foo=bar", [Lexer.Token("foo", 0, 0), Lexer.Token("=", 0, 3), Lexer.Token("bar", 0, 4)]),
        ("foo=123", [Lexer.Token("foo", ANY_POS), Lexer.Token("=", ANY_POS), Lexer.Token("123", ANY_POS)]),
        (
            'foo="abc"',
            [
                Lexer.Token("foo", ANY_POS),
                Lexer.Token("=", ANY_POS),
                Lexer.Token('"', ANY_POS),
                Lexer.Token("abc", ANY_POS),
                Lexer.Token('"', ANY_POS),
            ],
        ),
        (
            "foo[0]",
            [
                Lexer.Token("foo", ANY_POS),
                Lexer.Token("[", ANY_POS),
                Lexer.Token("0", ANY_POS),
                Lexer.Token("]", ANY_POS),
            ],
        ),
        ("!foo", [Lexer.Token("!", ANY_POS), Lexer.Token("foo", ANY_POS)]),
        ("NOT", [Lexer.Token("NOT", ANY_POS)]),
        ("prnt 123", [Lexer.Token("prnt", ANY_POS), Lexer.Token(" ", ANY_POS), Lexer.Token("123", ANY_POS)]),
        ("   ", [Lexer.Token(" ", ANY_POS), Lexer.Token(" ", ANY_POS), Lexer.Token(" ", ANY_POS)]),
        ("a=", [Lexer.Token("a", ANY_POS), Lexer.Token("=", ANY_POS)]),
        ("==", [Lexer.Token("==", ANY_POS)]),
        ("===", [Lexer.Token("===", ANY_POS)]),
        ("!", [Lexer.Token("!", ANY_POS)]),
        ("!=", [Lexer.Token("!=", ANY_POS)]),
        ("!==", [Lexer.Token("!==", ANY_POS)]),
        ("[", [Lexer.Token("[", ANY_POS)]),
        ("[[", [Lexer.Token("[", ANY_POS), Lexer.Token("[", ANY_POS)]),
        ("]", [Lexer.Token("]", ANY_POS)]),
        ("]]", [Lexer.Token("]", ANY_POS), Lexer.Token("]", ANY_POS)]),
        ("[]", [Lexer.Token("[", ANY_POS), Lexer.Token("]", ANY_POS)]),
        (
            "[[]]",
            [
                Lexer.Token("[", ANY_POS),
                Lexer.Token("[", ANY_POS),
                Lexer.Token("]", ANY_POS),
                Lexer.Token("]", ANY_POS),
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
