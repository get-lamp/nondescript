from src.lexer import Lexer
from src.lang import Lang
import pytest


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
    ("source", "words", "types"),
    [
        [(
            "foo=bar",
            ["foo", "=", "bar"],
            [Lang.Identifier, Lang.Assign, Lang.Identifier]
        ),
        (
            "foo=123",
            ["foo", "=", "123"],
            [Lang.Identifier, Lang.Assign, Lang.Integer]),
        (
            'foo="abc"',
            ["foo", "=", '"', 'abc', '"'],
            [Lang.Identifier, Lang.Assign, Lang.DoubleQuote, Lang.Identifier, Lang.DoubleQuote],
        ),
        (
            "foo[0]",
            ['foo', '[', '0', ']'],
            [Lang.Identifier, Lang.Bracket, Lang.Integer, Lang.Bracket]
        ),
        (
            "!foo",
            ['!', 'foo'],
            [Lang.UnaryOperator, Lang.Identifier]
        ),
        (
            "NOT",
            ["NOT"],
            [Lang.Not]
        ),
        (
            "prnt 123",
            ["prnt", "123"],
            [Lang.Prnt, Lang.Space, Lang.Integer]
        ),
        (
            "   ",
            [   ],
            [Lang.Space, Lang.Space, Lang.Space]
        ),
        (
            "a=",
            ['a', '='],
            [Lang.Identifier, Lang.Assign]
        ),
        (
            "==",
            ['=='],
            [Lang.Equal]
        ),
        (
            "===",
            ['==='],
            [Lang.EqualStrict]
        ),
        (
            "!",
            ['!'],
            [Lang.UnaryOperator]
        ),
        (
            "!=",
            ['!='],
            [Lang.Inequal]
        ),
        (
            "!==",
            ['!=='],
            [Lang.InequalStrict]
        )][0]
    ],
)
def test_next(source, words, types):
    lexer = Lexer(Lang, source)

    for i in range(len(types)):
        token = lexer.next()
        assert token.word == words[i]
        assert type(token) is types[i]
