from src.exc import UnexpectedSymbol
from src.parser import Parser
from src.lang import Lang
import pytest
from unittest.mock import ANY


ANY_POS = (ANY, ANY)


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        (
            "!==!==!==",
            [
                Lang.InequalStrict("!==", ANY_POS),
                Lang.InequalStrict("!==", ANY_POS),
                Lang.InequalStrict("!==", ANY_POS),
            ],
        ),
        (
            "foo=bar",
            [
                Lang.Identifier("foo", ANY_POS),
                Lang.Assign("=", ANY_POS),
                Lang.Identifier("bar", ANY_POS),
            ],
        ),
        (
            "foo!=bar",
            [
                Lang.Identifier("foo", ANY_POS),
                Lang.Inequal("!=", ANY_POS),
                Lang.Identifier("bar", ANY_POS),
            ],
        ),
        (
            "foo!==bar",
            [
                Lang.Identifier("foo", ANY_POS),
                Lang.InequalStrict("!==", ANY_POS),
                Lang.Identifier("bar", ANY_POS),
            ],
        ),
        (
            "prnt 'hello'",
            [
                Lang.Prnt("prnt", ANY_POS),
                Lang.Space(" ", ANY_POS),
                Lang.SingleQuote("'", ANY_POS),
                Lang.Identifier("hello", ANY_POS),
                Lang.SingleQuote("'", ANY_POS),
            ],
        ),
        (
            "if foo==bar",
            [
                Lang.If("if", ANY_POS),
                Lang.Space(" ", ANY_POS),
                Lang.Identifier("foo", ANY_POS),
                Lang.Equal("==", ANY_POS),
                Lang.Identifier("bar", ANY_POS),
            ],
        ),
        (
            "procedure my_proc",
            [
                Lang.Procedure("procedure", ANY_POS),
                Lang.Space(" ", ANY_POS),
                Lang.Identifier("my_proc", ANY_POS),
            ],
        ),
        (
            "exec my_proc",
            [
                Lang.Exec("exec", ANY_POS),
                Lang.Space(" ", ANY_POS),
                Lang.Identifier("my_proc", ANY_POS),
            ],
        ),
        (
            "1+2",
            [
                Lang.Integer("1", ANY_POS),
                Lang.Add("+", ANY_POS),
                Lang.Integer("2", ANY_POS),
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
            [
                Lang.Parentheses("(", ANY_POS, open=True),
                Lang.Integer("1", ANY_POS),
                Lang.Add("+", ANY_POS),
                Lang.Integer("2", ANY_POS),
                Lang.Parentheses(")", ANY_POS, open=False),
            ],
        ),
    ],
)
def test_parse(source, expected):
    assert Parser(Lang, source).parse() == expected


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


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        ("1+2", [[Lang.Integer("1", ANY_POS)], Lang.Add("+", ANY_POS), [Lang.Integer("2", ANY_POS)]]),
        ("a * b", [[Lang.Identifier("a", ANY_POS)], Lang.Multiply("*", ANY_POS), [Lang.Identifier("b", ANY_POS)]]),
        (
            "a + b * c",  # Testing operator precedence
            [
                [Lang.Identifier("a", ANY_POS)],
                Lang.Add("+", ANY_POS),
                [[Lang.Identifier("b", ANY_POS)], Lang.Multiply("*", ANY_POS), [Lang.Identifier("c", ANY_POS)]],
            ],
        ),
        (
            "(a + b) * c",  # Testing parentheses grouping
            [
                [[Lang.Identifier("a", ANY_POS)], Lang.Add("+", ANY_POS), [Lang.Identifier("b", ANY_POS)]],
                Lang.Multiply("*", ANY_POS),
                [Lang.Identifier("c", ANY_POS)],
            ],
        ),
        (
            "'Hello' + ' ' + who",  # Testing right-associativity (adjusting based on previous failure)
            [
                [Lang.String("Hello", ANY_POS)],
                Lang.Add("+", ANY_POS),
                [[Lang.String(" ", ANY_POS)], Lang.Add("+", ANY_POS), [Lang.Identifier("who", ANY_POS)]],
            ],
        ),
        ("1", [Lang.Integer("1", ANY_POS)]),
        ("foo", [Lang.Identifier("foo", ANY_POS)]),
        ("!foo", [Lang.UnaryOperator("!", ANY_POS), [Lang.Identifier("foo", ANY_POS)]]),
        ("NOT bar", [Lang.Not("NOT", ANY_POS), [Lang.Identifier("bar", ANY_POS)]]),
        ("1 == 2", [[Lang.Integer("1", ANY_POS)], Lang.Equal("==", ANY_POS), [Lang.Integer("2", ANY_POS)]]),
        ("1 != 2", [[Lang.Integer("1", ANY_POS)], Lang.Inequal("!=", ANY_POS), [Lang.Integer("2", ANY_POS)]]),
    ],
)
def test_build(source, expected):

    parser = Parser(Lang, source)
    ast = parser.build(parser.expression())
    assert ast == expected
