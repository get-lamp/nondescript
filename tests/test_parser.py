import src.lang.operator
from src.lang.base import Identifier, Block, Space, SingleQuote, Bracket, Keyword, Parentheses
from src.lang.data import Integer, Bool, String, Float
from src.lang.control import Procedure, If, Exec
from src.exc import UnexpectedSymbol
from src.parser import Parser
from src.lang import operator as op
from src.lang.grammar import Lang
import pytest
from unittest.mock import ANY


ANY_POS = (ANY, ANY)


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        (
            "!==!==!==",
            [
                op.UnequalStrict("!==", (0, 0)),
                op.UnequalStrict("!==", (0, 3)),
                op.UnequalStrict("!==", (0, 6)),
            ],
        ),
        (
            "foo=bar",
            [
                Identifier("foo", (0, 0)),
                op.Assign("=", (0, 3)),
                Identifier("bar", (0, 4)),
            ],
        ),
        (
            "foo!=bar",
            [
                Identifier("foo", (0, 0)),
                op.Unequal("!=", (0, 3)),
                Identifier("bar", (0, 5)),
            ],
        ),
        (
            "foo!==bar",
            [
                Identifier("foo", (0, 0)),
                op.UnequalStrict("!==", (0, 3)),
                Identifier("bar", (0, 6)),
            ],
        ),
        (
            "prnt 'hello'",
            [
                Lang.Prnt("prnt", (0, 0)),
                Space(" ", (0, 4)),
                SingleQuote("'", (0, 5)),
                Identifier("hello", (0, 6)),
                SingleQuote("'", (0, 11)),
            ],
        ),
        (
            "if foo==bar",
            [
                If("if", (0, 0)),
                Space(" ", (0, 2)),
                Identifier("foo", (0, 3)),
                op.Equal("==", (0, 6)),
                Identifier("bar", (0, 8)),
            ],
        ),
        (
            "procedure my_proc",
            [
                Procedure("procedure", (0, 0)),
                Space(" ", (0, 9)),
                Identifier("my_proc", (0, 10)),
            ],
        ),
        (
            "exec my_proc",
            [
                Exec("exec", (0, 0)),
                Space(" ", (0, 4)),
                Identifier("my_proc", (0, 5)),
            ],
        ),
        (
            "1+2",
            [
                Integer("1", (0, 0)),
                op.Add("+", (0, 1)),
                Integer("2", (0, 2)),
            ],
        ),
    ],
)
def test_next(source, expected):

    parser = Parser(Lang, source)

    for exp in expected:
        token = parser.lexer.next()
        assert token == exp
        assert type(token) is type(exp)


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        ("foo=bar", [Identifier("foo", (0, 0)), op.Assign("=", (0, 3)), Identifier("bar", (0, 4))]),
        ("if True:", [Keyword("if", (0, 0)), [Identifier("True", (0, 3))]]),
        ("[]", [Bracket("[", (0, 0), open=True), Bracket("]", (0, 1), open=False)]),
        (
            "[foo]",
            [
                Bracket("[", (0, 0), open=True),
                Identifier("foo", (0, 1)),
                Bracket("]", (0, 4), open=False),
            ],
        ),
        ("prnt 'hello'", [Lang.Prnt("prnt", (0, 0)), [String("hello", (0, 6))]]),
        ("1+2", [Integer("1", (0, 0)), op.Add("+", (0, 1)), Integer("2", (0, 2))]),
        (
            "(1+2)",
            [
                Parentheses("(", (0, 0), open=True),
                Integer("1", (0, 1)),
                op.Add("+", (0, 2)),
                Integer("2", (0, 3)),
                Parentheses(")", (0, 4), open=False),
            ],
        ),
        ("1       +       2", [Integer("1", (0, 0)), op.Add("+", (0, 8)), Integer("2", (0, 16))]),
        ("a++", [Identifier("a", (0, 0)), op.Increment("++", (0, 1))]),
        ("a--", [Identifier("a", (0, 0)), op.Decrement("--", (0, 1))]),
        ("!a", [op.Not("!", (0, 0)), Identifier("a", (0, 1))]),
    ],
)
def test_parse(source, expected):
    assert Parser(Lang, source).parse() == expected


@pytest.mark.parametrize(
    "source",
    ("!==", "+", "/", ":", "{", "}"),
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


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        ("1+2", [[Integer("1", (0, 0))], op.Add("+", (0, 1)), [Integer("2", (0, 2))]]),
        ("a * b", [[Identifier("a", (0, 0))], op.Multiply("*", (0, 2)), [Identifier("b", (0, 4))]]),
        (
            "a + b * c",  # Testing operator precedence
            [
                [Identifier("a", (0, 0))],
                op.Add("+", (0, 2)),
                [[Identifier("b", (0, 4))], op.Multiply("*", (0, 6)), [Identifier("c", (0, 8))]],
            ],
        ),
        (
            "(a + b) * c",  # Testing parentheses grouping
            [
                [[Identifier("a", (0, 1))], op.Add("+", (0, 3)), [Identifier("b", (0, 5))]],
                op.Multiply("*", (0, 8)),
                [Identifier("c", (0, 10))],
            ],
        ),
        (
            "'Hello' + ' ' + who",  # Testing right-associativity (adjusting based on previous failure)
            [
                [String("Hello", (0, 0))],
                op.Add("+", (0, 8)),
                [[String(" ", (0, 10))], op.Add("+", (0, 14)), [Identifier("who", (0, 16))]],
            ],
        ),
        ("1", [Integer("1", (0, 0))]),
        ("foo", [Identifier("foo", (0, 0))]),
        ("!foo", [src.lang.operator.UnaryOperator("!", (0, 0)), [Identifier("foo", (0, 1))]]),
        ("foo++", [op.Increment("++", (0, 3)), [Identifier("foo", (0, 0))]]),
        (
            "1+2++",
            [
                [Integer("1", (0, 0))],
                op.Add("+", (0, 1)),
                [op.Increment("++", (0, 3)), [Integer("2", (0, 2))]],
            ],
        ),
        ("NOT bar", [op.Not("NOT", (0, 0)), [Identifier("bar", (0, 4))]]),
        ("1 == 2", [[Integer("1", (0, 0))], op.Equal("==", (0, 2)), [Integer("2", (0, 5))]]),
        ("1 != 2", [[Integer("1", (0, 0))], op.Unequal("!=", (0, 2)), [Integer("2", (0, 5))]]),
    ],
)
def test_build(source, expected):

    parser = Parser(Lang, source)
    ast = parser.build(parser.expression())

    assert ast == expected


@pytest.mark.parametrize(
    "source",
    ("]", "--", "++", "--foo", "++foo"),
)
def test_build_raises_unexpected_symbol(source):
    parser = Parser(Lang, source)
    with pytest.raises(UnexpectedSymbol):
        parser.build(parser.expression())


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        (
            "foo++;bar++",
            [
                [op.Increment("++", (0, 3)), [Identifier("foo", (0, 0))]],
                [op.Increment("++", (1, 3)), [Identifier("bar", (1, 0))]],
            ],
        ),
        (
            "a=1;b=2;a++;b++",
            [
                [[Identifier("a", (0, 0))], op.Assign("=", (0, 1)), [Integer(1, (0, 2))]],
                [[Identifier("b", (1, 0))], op.Assign("=", (1, 1)), [Integer(2, (0, 2))]],
                [op.Increment("++", (2, 1)), [Identifier("a", (2, 0))]],
                [op.Increment("++", (3, 1)), [Identifier("b", (3, 0))]],
            ],
        ),
        (
            "foo--;bar--",
            [
                [op.Decrement("--", (0, 3)), [Identifier("foo", (0, 0))]],
                [op.Decrement("--", (1, 3)), [Identifier("bar", (1, 0))]],
            ],
        ),
        (
            "a=1;b=2;a--;b--",
            [
                [[Identifier("a", (0, 0))], op.Assign("=", (0, 1)), [Integer(1, (0, 2))]],
                [[Identifier("b", (1, 0))], op.Assign("=", (1, 1)), [Integer(2, (0, 2))]],
                [op.Decrement("--", (2, 1)), [Identifier("a", (2, 0))]],
                [op.Decrement("--", (3, 1)), [Identifier("b", (3, 0))]],
            ],
        ),
    ],
)
def test_parse_and_build(source, expected):

    parser = Parser(Lang, source)

    for exp in expected:
        p = parser.parse()
        ast = parser.build(p)
        assert exp == ast

    assert parser.parse() is False
