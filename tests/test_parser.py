from src.parser import Parser, BLOCK_MAIN
from src.lang import Lang
import pytest


@pytest.mark.parametrize(
    ("source", "words", "types"),
    [
        (
            "foo=bar",
            ["foo", "=", "bar"],
            [Lang.Identifier, Lang.Assign, Lang.Identifier],
        )
    ],
)
def test_next(source, words, types):

    parser = Parser(Lang, source)

    for i, word in enumerate(words):
        token = parser.lexer.next()
        breakpoint()
        # assert token.word == words[i]
        # assert type(token) is types[i]


@pytest.mark.parametrize(
    ("source", "words", "types"),
    [
        (
            "foo=bar",
            ["foo", "=", "bar"],
            [Lang.Identifier, Lang.Assign, Lang.Identifier],
        )
    ],
)
def test_parse(source, words, types):

    parser = Parser(Lang, source)

    assert parser.count == 0
    assert parser.tree == []
    assert parser.pending == []
    assert parser.blocks == [BLOCK_MAIN]

    sentence = parser.parse()

    for i, word in enumerate(sentence):
        assert sentence[i].word == words[i]
        assert type(sentence[i]) is types[i]
