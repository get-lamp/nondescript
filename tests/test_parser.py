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
