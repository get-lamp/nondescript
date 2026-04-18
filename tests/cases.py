COMPARISON = [
    "!==!==!=!====",
    "foo!=bar",
    "foo!==bar",
    "1 == 2",
    "1 != 2",
    "!==",
]

ASSIGNMENT = [
    "foo=bar",
    "a=1;b=2;a++;b++",
    "a=1;b=2;a--;b--",
]

ARITHMETIC = [
    "1+2",
    "1       +       2",
    "a * b",
    "a + b * c",
    "(a + b) * c",
    "(1+2)",
    "1",
]

UNARY = [
    "a++",
    "a--",
    "!a",
    "!foo",
    "foo++",
    "1+2++",
    "NOT bar",
]

CONTROL_FLOW = [
    "if foo==bar",
    "if TRUE:",
]

FUNCTION_DEF = [
    "def func a,b,c: end",
    "def func a,b,c\nend",
    "def func a\nend",
    "def func\nend",
    "def func a\nx=0\nend",
    "def func a,b,c\nx=0\nend",
    "def func\nx=0;y=1;z=2\nend",
]

CALLS = [
    "exec my_proc",
]

PROCEDURES = [
    "procedure my_proc",
]

LITERALS = [
    "prnt 'hello'",
    "'Hello' + ' ' + who",
    "foo",
]

COLLECTIONS = [
    "[]",
    "[foo]",
]

TOKENS = [
    "+",
    "/",
    ":",
    "{",
    "}",
    "[",
    "]",
]

SEQUENCES = [
    "foo++;bar++",
    "foo--;bar--",
]

EXPRESSIONS_SOURCE = (
    COMPARISON
    + ASSIGNMENT
    + ARITHMETIC
    + UNARY
    + CONTROL_FLOW
    + FUNCTION_DEF
    + CALLS
    + PROCEDURES
    + LITERALS
    + COLLECTIONS
    + TOKENS
    + SEQUENCES
)


def build_test_cases(expressions_source, groups):
    if len(expressions_source) != len(groups):
        msg = [
            "Length mismatch in EXPRESSION_SOURCE vs groups",
            f"- expressions_source: {len(expressions_source)} items",
            f"- groups: {len(groups)} items",
        ]

        min_len = min(len(expressions_source), len(groups))

        # show aligned pairs up to the shortest length
        if min_len:
            msg.append("\nAligned preview (first mismatches may be below):")
            for i in range(min_len):
                msg.append(f"  [{i}] {expressions_source[i]!r}")

        # show extras on either side
        if len(expressions_source) > min_len:
            msg.append("\nExtra expressions_source items:")
            for i in range(min_len, len(expressions_source)):
                msg.append(f"  [{i}] {expressions_source[i]!r}")

        if len(groups) > min_len:
            msg.append("\nExtra groups items (showing lengths only):")
            for i in range(min_len, len(groups)):
                msg.append(f"  [{i}] len={len(groups[i])}")

        raise ValueError("\n".join(msg))

    return list(zip(expressions_source, groups))
