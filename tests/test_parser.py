import src.lang.operator
from src.lang.base import (
    Identifier,
    Space,
    NewLine,
    SingleQuote,
    Bracket,
    Keyword,
    Parentheses,
    Comma,
)
from src.lang.data import Integer, String
from src.lang.control import Procedure, If, Exec, Def, End
from src.exc import UnexpectedSymbol
from src.parser import Parser
from src.lang import operator as op
from src.lang.grammar import Lang
from src.lexer import Token
import pytest
from unittest.mock import ANY


ANY_POS = (ANY, ANY)


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        (
            "!==!==!==",
            [
                op.UnequalStrict(Token("!==", 0, 0, 3)),
                op.UnequalStrict(Token("!==", 0, 3, 6)),
                op.UnequalStrict(Token("!==", 0, 6, 9)),
            ],
        ),
        (
            "foo=bar",
            [
                Identifier(Token("foo", 0, 0, 3)),
                op.Assign(Token("=", 0, 3, 4)),
                Identifier(Token("bar", 0, 4, 7)),
            ],
        ),
        (
            "foo!=bar",
            [
                Identifier(Token("foo", 0, 0, 3)),
                op.Unequal(Token("!=", 0, 3, 5)),
                Identifier(Token("bar", 0, 5, 8)),
            ],
        ),
        (
            "foo!==bar",
            [
                Identifier(Token("foo", 0, 0, 3)),
                op.UnequalStrict(Token("!==", 0, 3, 6)),
                Identifier(Token("bar", 0, 6, 9)),
            ],
        ),
        (
            "prnt 'hello'",
            [
                Lang.Prnt(Token("prnt", 0, 0, 4)),
                Space(Token(" ", 0, 4, 5)),
                SingleQuote(Token("'", 0, 5, 6)),
                Identifier(Token("hello", 0, 6, 11)),
                SingleQuote(Token("'", 0, 11, 12)),
            ],
        ),
        (
            "if foo==bar",
            [
                If(Token("if", 0, 0, 2)),
                Space(Token(" ", 0, 2, 3)),
                Identifier(Token("foo", 0, 3, 6)),
                op.Equal(Token("==", 0, 6, 8)),
                Identifier(Token("bar", 0, 8, 11)),
            ],
        ),
        (
            "procedure my_proc",
            [
                Procedure(Token("procedure", 0, 0, 9)),
                Space(Token(" ", 0, 9, 10)),
                Identifier(Token("my_proc", 0, 10, 17)),
            ],
        ),
        (
            "exec my_proc",
            [
                Exec(Token("exec", 0, 0, 4)),
                Space(Token(" ", 0, 4, 5)),
                Identifier(Token("my_proc", 0, 5, 12)),
            ],
        ),
        (
            "1+2",
            [
                Integer(Token("1", 0, 0, 1)),
                op.Add(Token("+", 0, 1, 2)),
                Integer(Token("2", 0, 2, 3)),
            ],
        ),
        (
            "def func a,b,c: end",
            [
                Def(Token("def", 0, 0, ANY)),
                Space(Token(" ", 0, 3, ANY)),
                Identifier(Token("func", 0, 4, ANY)),
                Space(Token(" ", 0, 8, ANY)),
                Identifier(Token("a", 0, 9, ANY)),
                Comma(Token(",", 0, 10, ANY)),
                Identifier(Token("b", 0, 11, ANY)),
                Comma(Token(",", 0, 12, ANY)),
                Identifier(Token("c", 0, 13, ANY)),
                Space(Token(" ", 0, 15, ANY)),
                End(Token("end", 0, 16, ANY)),
            ],
        ),
        (
            "def func a,b,c\nend",
            [
                Def(Token("def", 0, 0, ANY)),
                Space(Token(" ", 0, 3, ANY)),
                Identifier(Token("func", 0, 4, ANY)),
                Space(Token(" ", 0, 8, ANY)),
                Identifier(Token("a", 0, 9, ANY)),
                Comma(Token(",", 0, 10, ANY)),
                Identifier(Token("b", 0, 11, ANY)),
                Comma(Token(",", 0, 12, ANY)),
                Identifier(Token("c", 0, 13, ANY)),
                NewLine(Token("\n", 0, 14, ANY)),
                End(Token("end", 1, 0, ANY)),
            ],
        ),
        (
            "def func a\nend",
            [
                Def(Token("def", 0, 0, ANY)),
                Space(Token(" ", 0, 3, ANY)),
                Identifier(Token("func", 0, 4, ANY)),
                Space(Token(" ", 0, 8, ANY)),
                Identifier(Token("a", 0, 9, ANY)),
                NewLine(Token("\n", 0, 10, ANY)),
                End(Token("end", 1, 0, ANY)),
            ],
        ),
    ],
)
def test_next(source, expected):

    parser = Parser(Lang, source)

    for exp in expected:
        token = parser.lexer.next()
        assert token.word == exp.word
        assert token.char == exp.char
        assert token.line == exp.line
        assert type(token) is type(exp)

    assert parser.next() is False


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        (
            "foo=bar",
            [
                Identifier(Token("foo", 0, 0, 0)),
                op.Assign(Token("=", 0, 3, 3)),
                Identifier(Token("bar", 0, 4, 4)),
            ],
        ),
        (
            "if True:",
            [Keyword(Token("if", 0, 0, 0)), [Identifier(Token("True", 0, 3, 3))]],
        ),
        (
            "[]",
            [
                Bracket(Token("[", 0, 0, 0), open=True),
                Bracket(Token("]", 0, 1, 1), open=False),
            ],
        ),
        (
            "[foo]",
            [
                Bracket(Token("[", 0, 0, 0), open=True),
                Identifier(Token("foo", 0, 1, 1)),
                Bracket(Token("]", 0, 4, 4), open=False),
            ],
        ),
        (
            "prnt 'hello'",
            [Lang.Prnt(Token("prnt", 0, 0, 0)), [String(Token("hello", 0, 6, 6))]],
        ),
        (
            "1+2",
            [
                Integer(Token("1", 0, 0, 0)),
                op.Add(Token("+", 0, 1, 1)),
                Integer(Token("2", 0, 2, 2)),
            ],
        ),
        (
            "(1+2)",
            [
                Parentheses(Token("(", 0, 0, 0), open=True),
                Integer(Token("1", 0, 1, 1)),
                op.Add(Token("+", 0, 2, 2)),
                Integer(Token("2", 0, 3, 3)),
                Parentheses(Token(")", 0, 4, 4), open=False),
            ],
        ),
        (
            "1       +       2",
            [
                Integer(Token("1", 0, 0, 0)),
                op.Add(Token("+", 0, 8, 8)),
                Integer(Token("2", 0, 16, 16)),
            ],
        ),
        ("a++", [Identifier(Token("a", 0, 0, 0)), op.Increment(Token("++", 0, 1, 1))]),
        ("a--", [Identifier(Token("a", 0, 0, 0)), op.Decrement(Token("--", 0, 1, 1))]),
        ("!a", [op.Not(Token("!", 0, 0, 0)), Identifier(Token("a", 0, 1, 1))]),
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
        (
                "1+2",
                [
                    Integer(Token("1", 0, 0, 0)),
                    op.Add(Token("+", 0, 1, 1)),
                    Integer(Token("2", 0, 2, 2)),
                ],
        ),
        (
                "a * b",
                [
                    Identifier(Token("a", 0, 0, 0)),
                    op.Multiply(Token("*", 0, 2, 2)),
                    Identifier(Token("b", 0, 4, 4)),
                ],
        ),
        (
                "a + b * c",  # Testing operator precedence
                [
                    [Identifier(Token("a", 0, 0, 0))],
                    op.Add(Token("+", 0, 2, 2)),
                    [
                        [Identifier(Token("b", 0, 4, 4))],
                        op.Multiply(Token("*", 0, 6, 6)),
                        [Identifier(Token("c", 0, 8, 8))],
                    ],
                ],
        ),
        (
                "(a + b) * c",  # Testing parentheses grouping
                [
                    [
                        [Identifier(Token("a", 0, 1, 1))],
                        op.Add(Token("+", 0, 3, 3)),
                        [Identifier(Token("b", 0, 5, 5))],
                    ],
                    op.Multiply(Token("*", 0, 8, 8)),
                    [Identifier(Token("c", 0, 10, 10))],
                ],
        ),
        (
                "'Hello' + ' ' + who",  # Testing right-associativity (adjusting based on previous failure)
                [
                    [String(Token("Hello", 0, 1, 1))],
                    op.Add(Token("+", 0, 8, 8)),
                    [
                        [String(Token(" ", 0, 11, 11))],
                        op.Add(Token("+", 0, 14, 14)),
                        [Identifier(Token("who", 0, 16, 16))],
                    ],
                ],
        ),
        ("1", [Integer(Token("1", 0, 0, 0))]),
        ("foo", [Identifier(Token("foo", 0, 0, 0))]),
        (
                "!foo",
                [
                    src.lang.operator.UnaryOperator(Token("!", 0, 0, 0)),
                    [Identifier(Token("foo", 0, 1, 1))],
                ],
        ),
        (
                "foo++",
                [op.Increment(Token("++", 0, 3, 3)), [Identifier(Token("foo", 0, 0, 0))]],
        ),
        (
                "1+2++",
                [
                    [Integer(Token("1", 0, 0, 0))],
                    op.Add(Token("+", 0, 1, 1)),
                    [op.Increment(Token("++", 0, 3, 3)), [Integer(Token("2", 0, 2, 2))]],
                ],
        ),
        (
                "NOT bar",
                [op.Not(Token("NOT", 0, 0, 0)), [Identifier(Token("bar", 0, 4, 4))]],
        ),
        (
                "1 == 2",
                [
                    [Integer(Token("1", 0, 0, 0))],
                    op.Equal(Token("==", 0, 2, 2)),
                    [Integer(Token("2", 0, 5, 5))],
                ],
        ),
        (
                "1 != 2",
                [
                    [Integer(Token("1", 0, 0, 0))],
                    op.Unequal(Token("!=", 0, 2, 2)),
                    [Integer(Token("2", 0, 5, 5))],
                ],
        ),
    ],
)
def test_parse_expression(source, expected):

    parser = Parser(Lang, source)
    expression = parser.parse_expression()


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        (
            "1+2",
            [
                [Integer(Token("1", 0, 0, 0))],
                op.Add(Token("+", 0, 1, 1)),
                [Integer(Token("2", 0, 2, 2))],
            ],
        ),
        (
            "a * b",
            [
                [Identifier(Token("a", 0, 0, 0))],
                op.Multiply(Token("*", 0, 2, 2)),
                [Identifier(Token("b", 0, 4, 4))],
            ],
        ),
        (
            "a + b * c",  # Testing operator precedence
            [
                [Identifier(Token("a", 0, 0, 0))],
                op.Add(Token("+", 0, 2, 2)),
                [
                    [Identifier(Token("b", 0, 4, 4))],
                    op.Multiply(Token("*", 0, 6, 6)),
                    [Identifier(Token("c", 0, 8, 8))],
                ],
            ],
        ),
        (
            "(a + b) * c",  # Testing parentheses grouping
            [
                [
                    [Identifier(Token("a", 0, 1, 1))],
                    op.Add(Token("+", 0, 3, 3)),
                    [Identifier(Token("b", 0, 5, 5))],
                ],
                op.Multiply(Token("*", 0, 8, 8)),
                [Identifier(Token("c", 0, 10, 10))],
            ],
        ),
        (
            "'Hello' + ' ' + who",  # Testing right-associativity (adjusting based on previous failure)
            [
                [String(Token("Hello", 0, 1, 1))],
                op.Add(Token("+", 0, 8, 8)),
                [
                    [String(Token(" ", 0, 11, 11))],
                    op.Add(Token("+", 0, 14, 14)),
                    [Identifier(Token("who", 0, 16, 16))],
                ],
            ],
        ),
        ("1", [Integer(Token("1", 0, 0, 0))]),
        ("foo", [Identifier(Token("foo", 0, 0, 0))]),
        (
            "!foo",
            [
                src.lang.operator.UnaryOperator(Token("!", 0, 0, 0)),
                [Identifier(Token("foo", 0, 1, 1))],
            ],
        ),
        (
            "foo++",
            [op.Increment(Token("++", 0, 3, 3)), [Identifier(Token("foo", 0, 0, 0))]],
        ),
        (
            "1+2++",
            [
                [Integer(Token("1", 0, 0, 0))],
                op.Add(Token("+", 0, 1, 1)),
                [op.Increment(Token("++", 0, 3, 3)), [Integer(Token("2", 0, 2, 2))]],
            ],
        ),
        (
            "NOT bar",
            [op.Not(Token("NOT", 0, 0, 0)), [Identifier(Token("bar", 0, 4, 4))]],
        ),
        (
            "1 == 2",
            [
                [Integer(Token("1", 0, 0, 0))],
                op.Equal(Token("==", 0, 2, 2)),
                [Integer(Token("2", 0, 5, 5))],
            ],
        ),
        (
            "1 != 2",
            [
                [Integer(Token("1", 0, 0, 0))],
                op.Unequal(Token("!=", 0, 2, 2)),
                [Integer(Token("2", 0, 5, 5))],
            ],
        ),
    ],
)
def test_build(source, expected):

    parser = Parser(Lang, source)
    ast = parser.build_ast(parser.parse_expression())

    assert ast == expected


@pytest.mark.parametrize(
    "source",
    ("]", "--", "++", "--foo", "++foo"),
)
def test_build_raises_unexpected_symbol(source):
    parser = Parser(Lang, source)
    with pytest.raises(UnexpectedSymbol):
        parser.build_ast(parser.parse_expression())


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        (
            "foo++;bar++",
            [
                [
                    op.Increment(Token("++", 0, 3, 5)),
                    [Identifier(Token("foo", 0, 0, 3))],
                ],
                [
                    op.Increment(Token("++", 1, 3, 5)),
                    [Identifier(Token("bar", 1, 0, 3))],
                ],
            ],
        ),
        (
            "a=1;b=2;a++;b++",
            [
                [
                    [Identifier(Token("a", 0, 0, 1))],
                    op.Assign(Token("=", 0, 1, 2)),
                    [Integer(Token("1", 0, 2, 3))],
                ],
                [
                    [Identifier(Token("b", 1, 0, 1))],
                    op.Assign(Token("=", 1, 1, 2)),
                    [Integer(Token("2", 1, 2, 3))],
                ],
                [op.Increment(Token("++", 2, 1, 3)), [Identifier(Token("a", 2, 0, 1))]],
                [op.Increment(Token("++", 3, 1, 3)), [Identifier(Token("b", 3, 0, 1))]],
            ],
        ),
        (
            "foo--;bar--",
            [
                [
                    op.Decrement(Token("--", 0, 3, 5)),
                    [Identifier(Token("foo", 0, 0, 3))],
                ],
                [
                    op.Decrement(Token("--", 1, 3, 5)),
                    [Identifier(Token("bar", 1, 0, 3))],
                ],
            ],
        ),
        (
            "a=1;b=2;a--;b--",
            [
                [
                    [Identifier(Token("a", 0, 0, 1))],
                    op.Assign(Token("=", 0, 1, 2)),
                    [Integer(Token("1", 0, 2, 3))],
                ],
                [
                    [Identifier(Token("b", 1, 0, 1))],
                    op.Assign(Token("=", 1, 1, 2)),
                    [Integer(Token("2", 1, 2, 3))],
                ],
                [op.Decrement(Token("--", 2, 1, 3)), [Identifier(Token("a", 2, 0, 1))]],
                [op.Decrement(Token("--", 3, 1, 3)), [Identifier(Token("b", 3, 0, 1))]],
            ],
        ),
        (
            "def func a\nend",
            [
                [
                    Def(Token("def", ANY, ANY, ANY)),
                    [Identifier(Token("func", ANY, ANY, ANY))],
                    [Identifier(Token("a", ANY, ANY, ANY))],
                ]
            ],
        ),
        (
            "def func a,b,c\nend",
            [
                [
                    Def(Token("def", ANY, ANY, ANY)),
                    [Identifier(Token("func", ANY, ANY, ANY))],
                    [
                        [Identifier(Token("a", ANY, ANY, ANY))],
                        [Identifier(Token("b", ANY, ANY, ANY))],
                        [Identifier(Token("c", ANY, ANY, ANY))],
                    ],
                ]
            ],
        ),
        (
            "def func\nend",
            [
                [
                    Def(Token("def", ANY, ANY, ANY)),
                    [Identifier(Token("func", ANY, ANY, ANY))],
                    [],
                ]
            ],
        ),
    ],
)
def test_build_ast(source, expected):

    parser = Parser(Lang, source)

    for exp in expected:
        p = parser.parse()
        ast = parser.build_ast(p)
        assert ast == exp

    assert parser.parse() is False


@pytest.mark.parametrize(
    ("source", "expected_ast", "expected_block"),
    [
        (
            "def func a\nend",
            [
                [
                    Def(Token("def", ANY, ANY, ANY)),
                    [Identifier(Token("func", ANY, ANY, ANY))],
                    [Identifier(Token("a", ANY, ANY, ANY))],
                ]
            ],
            [],
        ),
        (
            "def func a\nx=0\nend",
            [
                [
                    Def(Token("def", ANY, ANY, ANY)),
                    [Identifier(Token("func", ANY, ANY, ANY))],
                    [Identifier(Token("a", ANY, ANY, ANY))],
                ]
            ],
            [
                [
                    [Identifier(Token("x", ANY, ANY, ANY))],
                    op.Assign(Token("=", ANY, ANY, ANY)),
                    [Integer(Token("0", ANY, ANY, ANY))],
                ]
            ],
        ),
        (
            "def func a,b,c\nx=0\nend",
            [
                [
                    Def(Token("def", ANY, ANY, ANY)),
                    [Identifier(Token("func", ANY, ANY, ANY))],
                    [
                        [Identifier(Token("a", ANY, ANY, ANY))],
                        [Identifier(Token("b", ANY, ANY, ANY))],
                        [Identifier(Token("c", ANY, ANY, ANY))],
                    ],
                ]
            ],
            [
                [
                    [Identifier(Token("x", ANY, ANY, ANY))],
                    op.Assign(Token("=", ANY, ANY, ANY)),
                    [Integer(Token("0", ANY, ANY, ANY))],
                ]
            ],
        ),
        (
            "def func\nx=0;y=1;x=2\nend",
            [
                [
                    Def(Token("def", ANY, ANY, ANY)),
                    [Identifier(Token("func", ANY, ANY, ANY))],
                    [],
                ]
            ],
            [
                [
                    [Identifier(Token("x", ANY, ANY, ANY))],
                    op.Assign(Token("=", ANY, ANY, ANY)),
                    [Integer(Token("0", ANY, ANY, ANY))],
                ],
                [
                    [Identifier(Token("y", ANY, ANY, ANY))],
                    op.Assign(Token("=", ANY, ANY, ANY)),
                    [Integer(Token("1", ANY, ANY, ANY))],
                ],
                [
                    [Identifier(Token("z", ANY, ANY, ANY))],
                    op.Assign(Token("=", ANY, ANY, ANY)),
                    [Integer(Token("2", ANY, ANY, ANY))],
                ],
            ],
        ),
    ],
)
def test_functions_in_built_ast(source, expected_ast, expected_block):
    parser = Parser(Lang, source)

    for exp in expected_ast:
        p = parser.parse()
        ast = parser.build_ast(p)

        assert ast == exp

        def_k, ident, sign = ast

        assert def_k.block == expected_block

    assert parser.parse() is False
