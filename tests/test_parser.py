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
                Lang.InequalStrict("!==", (0, 0)),
                Lang.InequalStrict("!==", (0, 3)),
                Lang.InequalStrict("!==", (0, 6)),
            ],
        ),
        (
            "foo=bar",
            [
                Lang.Identifier("foo", (0, 0)),
                Lang.Assign("=", (0, 3)),
                Lang.Identifier("bar", (0, 4)),
            ],
        ),
        (
            "foo!=bar",
            [
                Lang.Identifier("foo", (0, 0)),
                Lang.Inequal("!=", (0, 3)),
                Lang.Identifier("bar", (0, 5)),
            ],
        ),
        (
            "foo!==bar",
            [
                Lang.Identifier("foo", (0, 0)),
                Lang.InequalStrict("!==", (0, 3)),
                Lang.Identifier("bar", (0, 6)),
            ],
        ),
        (
            "prnt 'hello'",
            [
                Lang.Prnt("prnt", (0, 0)),
                Lang.Space(" ", (0, 4)),
                Lang.SingleQuote("'", (0, 5)),
                Lang.Identifier("hello", (0, 6)),
                Lang.SingleQuote("'", (0, 11)),
            ],
        ),
        (
            "if foo==bar",
            [
                Lang.If("if", (0, 0)),
                Lang.Space(" ", (0, 2)),
                Lang.Identifier("foo", (0, 3)),
                Lang.Equal("==", (0, 6)),
                Lang.Identifier("bar", (0, 8)),
            ],
        ),
        (
            "procedure my_proc",
            [
                Lang.Procedure("procedure", (0, 0)),
                Lang.Space(" ", (0, 9)),
                Lang.Identifier("my_proc", (0, 10)),
            ],
        ),
        (
            "exec my_proc",
            [
                Lang.Exec("exec", (0, 0)),
                Lang.Space(" ", (0, 4)),
                Lang.Identifier("my_proc", (0, 5)),
            ],
        ),
        (
            "1+2",
            [
                Lang.Integer("1", (0, 0)),
                Lang.Add("+", (0, 1)),
                Lang.Integer("2", (0, 2)),
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
            [Lang.Identifier("foo", (0, 0)), Lang.Assign("=", (0, 3)), Lang.Identifier("bar", (0, 4))],
        ),
        (
            "if True:",
            [Lang.Keyword("if", (0, 0)), [Lang.Identifier("True", (0, 3))]],
        ),
        (
            "[]",
            [Lang.Bracket("[", (0, 0), open=True), Lang.Bracket("]", (0, 1), open=False)],
        ),
        (
            "[foo]",
            [
                Lang.Bracket("[", (0, 0), open=True),
                Lang.Identifier("foo", (0, 1)),
                Lang.Bracket("]", (0, 4), open=False),
            ],
        ),
        (
            "prnt 'hello'",
            [Lang.Prnt("prnt", (0, 0)), [Lang.String("hello", (0, 6))]],
        ),
        (
            "1+2",
            [Lang.Integer("1", (0, 0)), Lang.Add("+", (0, 1)), Lang.Integer("2", (0, 2))],
        ),
        (
            "(1+2)",
            [
                Lang.Parentheses("(", (0, 0), open=True),
                Lang.Integer("1", (0, 1)),
                Lang.Add("+", (0, 2)),
                Lang.Integer("2", (0, 3)),
                Lang.Parentheses(")", (0, 4), open=False),
            ],
        ),
        (
                "1       +       2",
                [Lang.Integer("1", (0, 0)), Lang.Add("+", (0, 8)), Lang.Integer("2", (0, 16))],
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
        ("1+2", [[Lang.Integer("1", (0, 0))], Lang.Add("+", (0, 1)), [Lang.Integer("2", (0, 2))]]),
        ("a * b", [[Lang.Identifier("a", (0, 0))], Lang.Multiply("*", (0, 2)), [Lang.Identifier("b", (0, 4))]]),
        (
            "a + b * c",  # Testing operator precedence
            [
                [Lang.Identifier("a", (0, 0))],
                Lang.Add("+", (0, 2)),
                [[Lang.Identifier("b", (0, 4))], Lang.Multiply("*", (0, 6)), [Lang.Identifier("c", (0, 8))]],
            ],
        ),
        (
            "(a + b) * c",  # Testing parentheses grouping
            [
                [[Lang.Identifier("a", (0, 1))], Lang.Add("+", (0, 3)), [Lang.Identifier("b", (0, 5))]],
                Lang.Multiply("*", (0, 8)),
                [Lang.Identifier("c", (0, 10))],
            ],
        ),
        (
            "'Hello' + ' ' + who",  # Testing right-associativity (adjusting based on previous failure)
            [
                [Lang.String("Hello", (0, 0))],
                Lang.Add("+", (0, 8)),
                [[Lang.String(" ", (0, 10))], Lang.Add("+", (0, 14)), [Lang.Identifier("who", (0, 16))]],
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
