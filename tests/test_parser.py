from src.exc import UnexpectedSymbol
from src.parser import Parser
from src.lang import Lang
import pytest
from unittest.mock import ANY


ANY_POS = (ANY, ANY)


@pytest.mark.parametrize(
    ("source", "words", "types"),
    [
        (
            "!==!==!==",
            ["!==", "!==", "!=="],
            [Lang.InequalStrict, Lang.InequalStrict, Lang.InequalStrict],
        ),
        (
            "foo=bar",
            ["foo", "=", "bar"],
            [Lang.Identifier, Lang.Assign, Lang.Identifier],
        ),
        (
            "foo!=bar",
            ["foo", "!=", "bar"],
            [Lang.Identifier, Lang.Inequal, Lang.Identifier],
        ),
        (
            "foo!==bar",
            ["foo", "!==", "bar"],
            [Lang.Identifier, Lang.InequalStrict, Lang.Identifier],
        ),
        (
            "prnt 'hello'",
            ["prnt", " ", "'", "hello", "'"],
            [Lang.Prnt, Lang.Space, Lang.SingleQuote, Lang.Identifier, Lang.SingleQuote],
        ),
        (
            "if foo==bar",
            ["if", " ", "foo", "==", "bar"],
            [Lang.If, Lang.Space, Lang.Identifier, Lang.Equal, Lang.Identifier],
        ),
        (
            "procedure my_proc",
            ["procedure", " ", "my_proc"],
            [Lang.Procedure, Lang.Space, Lang.Identifier],
        ),
        (
            "exec my_proc",
            ["exec", " ", "my_proc"],
            [Lang.Exec, Lang.Space, Lang.Identifier],
        ),
        (
            "1+2",
            ["1", "+", "2"],
            [Lang.Integer, Lang.Add, Lang.Integer],
        ),
    ],
)
def test_next(source, words, types):

    parser = Parser(Lang, source)

    for i, word in enumerate(words):
        token = parser.lexer.next()
        assert token.word == words[i]
        assert type(token) is types[i]


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        (
            "foo=bar",
            [Lang.Identifier("foo", ANY_POS), Lang.Assign("=", ANY_POS), Lang.Identifier("bar", ANY_POS)],
        ),
        (
            "if True:",
            [Lang.Keyword("if", ANY_POS), [Lang.Identifier("True", ANY_POS)]],
        ),
        (
            "[]",
            [Lang.Bracket("[", ANY_POS, open=True), Lang.Bracket("]", ANY_POS, open=False)],
        ),
        (
            "[foo]",
            [
                Lang.Bracket("[", ANY_POS, open=True),
                Lang.Identifier("foo", ANY_POS),
                Lang.Bracket("]", ANY_POS, open=False),
            ],
        ),
        (
            "prnt 'hello'",
            [Lang.Prnt("prnt", ANY_POS), [Lang.String("hello", ANY_POS)]],
        ),
        (
            "1+2",
            [Lang.Integer("1", ANY_POS), Lang.Add("+", ANY_POS), Lang.Integer("2", ANY_POS)],
        ),
        (
            "(1+2)",
            [Lang.Parentheses("(", ANY_POS, open=True),
             Lang.Integer("1", ANY_POS),
             Lang.Add("+", ANY_POS),
             Lang.Integer("2", ANY_POS),
             Lang.Parentheses(")", ANY_POS, open=False)],
        ),
    ],
)
def test_parse(source, expected):

    parser = Parser(Lang, source)
    sentence = parser.parse()

    # breakpoint()

    assert sentence == expected


@pytest.mark.parametrize(
    "source",
    ("!==", "+", "!", "/", ":", "{", "}"),
)
def test_parse_returns_false(source):
    assert Parser(Lang, source).parse() is False


@pytest.mark.parametrize(
    "source",
    ("]",),
)
def test_parse_raises_unexpected_symbol(source):
    with pytest.raises(UnexpectedSymbol):
        Parser(Lang, source).parse()
