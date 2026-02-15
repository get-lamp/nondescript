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
                ("foo", 0, 0),
                (";", 0, 3),
                ("bar", 1, 0),
                (";", 1, 3),
                ("baz", 2, 0),
            ],
        ),
        (
            "foo\nbar\nbaz",
            [
                ("foo", 0, 0),
                ("\n", 0, 3),
                ("bar", 1, 0),
                ("\n", 1, 3),
                ("baz", 2, 0),
            ],
        ),
        (
            "foo bar baz",
            [
                ("foo", 0, 0),
                (" ", 0, 3),
                ("bar", 0, 4),
                (" ", 0, 7),
                ("baz", 0, 8),
            ],
        ),
        (
            "# ^ &",
            [
                ("#", 0, 0),
                (" ", 0, 1),
                ("^", 0, 2),
                (" ", 0, 3),
                ("&", 0, 4),
            ],
        ),
        (
            "0\n1\n2",
            [
                ("0", 0, 0),
                ("\n", 0, 1),
                ("1", 1, 0),
                ("\n", 1, 1),
                ("2", 2, 0),
            ],
        ),
        (
            "foo=bar",
            [
                ("foo", 0, 0),
                ("=", 0, 3),
                ("bar", 0, 4),
            ],
        ),
    ],
)
def test_scan_keeps_track_of_char_and_line_number(source, expected):

    _WORD, _LINE, _CHAR = (0, 1, 2)

    lexer = Lexer(Lang, source)

    for e in expected:
        token = lexer._scan()
        assert token.word == e[_WORD]
        assert token.line == e[_LINE]
        assert token.char == e[_CHAR]

    assert lexer._scan() is None


def test_scan_at_end_of_source():
    lexer = Lexer(Lang, "foo=bar")
    assert (lexer._scan()).word == "foo"
    assert (lexer._scan()).word == "="
    assert (lexer._scan()).word == "bar"
    assert lexer._scan() is None


@pytest.mark.parametrize(
    ('source', 'expected'),
    [
        ('foo=bar', [Lang.Identifier('foo', ANY_POS), Lang.Assign('=', ANY_POS), Lang.Identifier('bar', ANY_POS)]),
        ("foo=123", [Lang.Identifier('foo', ANY_POS), Lang.Assign('=', ANY_POS), Lang.Integer('123', ANY_POS)]),
        (
            'foo="abc"',
            [
                Lang.Identifier('foo', ANY_POS),
                Lang.Assign('=', ANY_POS),
                Lang.DoubleQuote('"', ANY_POS),
                Lang.Identifier('abc', ANY_POS),
                Lang.DoubleQuote('"', ANY_POS)
            ],
        ),
        ("foo[0]", [Lang.Identifier('foo', ANY_POS), Lang.Bracket, Lang.Integer, Lang.Bracket]),
        #("!foo", ["!", "foo"], [Lang.UnaryOperator, Lang.Identifier]),
        #("NOT", ["NOT"], [Lang.Not]),
        #("prnt 123", ["prnt", " ", "123"], [Lang.Prnt, Lang.Space, Lang.Integer]),
        #("   ", [" ", " ", " "], [Lang.Space, Lang.Space, Lang.Space]),
        #("a=", ["a", "="], [Lang.Identifier, Lang.Assign]),
        #("==", ["=="], [Lang.Equal]),
        #("===", ["==="], [Lang.EqualStrict]),
        #("!", ["!"], [Lang.UnaryOperator]),
        #("!=", ["!="], [Lang.Inequal]),
        #("!==", ["!=="], [Lang.InequalStrict]),
        #('[', [Lang.Bracket]),
        #('[[', [Lang.Bracket, Lang.Bracket]),
        #(']', [Lang.Bracket]),
        #(']]', [Lang.Bracket, Lang.Bracket]),
        #('[]', [Lang.Bracket, Lang.Bracket]),
        #('[[]]', [Lang.Bracket, Lang.Bracket, Lang.Bracket, Lang.Bracket]),
    ],
)
def test_next(source, expected):
    lexer = Lexer(Lang, source)

    for exp in expected:
        token = lexer.next()
        assert token == exp

    # assert it ends when we expect it
    assert lexer.next() is False
