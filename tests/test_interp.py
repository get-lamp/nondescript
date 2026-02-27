import pytest

from src.exc import EOF
from src.interp import Interpreter
from src.lang.control import Def

# --- Constants for sample file paths ---
ASSIGNMENT_AND_PRINT = "tests/sample/assignment_and_print.ns"
PROCEDURE = "tests/sample/procedure.ns"
FUNCTION_WITH_RETURN = "tests/sample/function_with_return.ns"
ARITHMETIC_EXPRESSIONS = "tests/sample/arithmetic_expressions.ns"
IF_ELSE_TRUE = "tests/sample/if_else_true.ns"
IF_ELSE_FALSE = "tests/sample/if_else_false.ns"
NESTED_STRUCTURES = "tests/sample/nested_structures.ns"
SAMPLE = "tests/sample/sample.ns"


def test_assignment_and_print():
    """Tests variable assignment and printing."""
    interp = Interpreter()
    interp.read(ASSIGNMENT_AND_PRINT, is_file=True)

    try:
        while True:
            interp.exec_next()
    except EOF:
        pass

    snapshot = Interpreter.Snapshot(interp)
    assert snapshot["Pointer"] == len(interp.memory.instr)
    assert snapshot["Scope"][0]["who"] == "World"
    assert snapshot["Instruction"] is None
    assert snapshot["Last result"] is None
    assert len(snapshot["Block stack"]) == 1
    assert snapshot["Stack"] == []
    assert snapshot["Ctrl stack"] == [True]


def test_procedure():
    """Tests a simple procedure definition and execution."""
    interp = Interpreter()
    interp.read(PROCEDURE, is_file=True)

    # Before 'exec test'
    interp.exec_next()  # 'procedure test'
    snapshot = Interpreter.Snapshot(interp)
    assert (
        snapshot["Pointer"] == 5
    )  # After defining the procedure, pointer moves to 'exec test'
    assert "test" in snapshot["Scope"][0]

    # Execute 'exec test'
    interp.exec_next()
    snapshot = Interpreter.Snapshot(interp)

    # Inside the procedure, at the first 'prnt 9'
    assert (
        snapshot["Pointer"] == 1
    )  # Pointer is at the first instruction *inside* the procedure (prnt 9)
    assert len(snapshot["Scope"]) == 2
    # assert snapshot["Block stack"] == ["<main>", snapshot["Scope"][1]["test"]]
    assert snapshot["Stack"] == [{"ret_addr": 5}]


def test_function_with_return():
    """Tests a function with parameters and a return value."""
    interp = Interpreter()
    interp.read(FUNCTION_WITH_RETURN, is_file=True)

    try:
        while True:
            interp.exec_next()
    except EOF:
        pass

    snapshot = Interpreter.Snapshot(interp)
    assert snapshot["Pointer"] == len(interp.memory.instr)
    assert snapshot["Scope"][0]["r"] == 6
    assert isinstance(snapshot["Scope"][0]["func"], Def)
    assert snapshot["Instruction"] is None
    assert snapshot["Last result"] is None


def test_arithmetic_expressions():
    """Tests simple and complex arithmetic expressions."""
    interp = Interpreter()
    interp.read(ARITHMETIC_EXPRESSIONS, is_file=True)

    try:
        while True:
            interp.exec_next()
    except EOF:
        pass

    snapshot = Interpreter.Snapshot(interp)
    assert snapshot["Pointer"] == len(interp.memory.instr)
    assert snapshot["Scope"][0]["z"] == 80.0
    assert snapshot["Instruction"] is None
    assert snapshot["Last result"] is None


def test_if_else_true_path():
    """Tests a basic if/else control flow example."""
    interp = Interpreter()
    interp.read(IF_ELSE_TRUE, is_file=True)
    # TODO: implement a test that runs the entire sample and check the interp final state
    # The true path is expected to be executed


def test_if_else_false_path():
    """Tests a basic if/else control flow example."""
    interp = Interpreter()
    interp.read(IF_ELSE_FALSE, is_file=True)
    # TODO: implement a test that runs the entire sample and check the interp final state
    # The false path is expected to be executed


def test_if_else_true_path_step_by_step():
    """Tests a basic if/else control flow example."""
    interp = Interpreter()
    interp.read(IF_ELSE_TRUE, is_file=True)
    # TODO implement a test that runs the sample step by step and checks
    # The true path is expected to be executed


def test_if_else_false_path_step_by_step():
    """Tests a basic if/else control flow example."""
    interp = Interpreter()
    interp.read(IF_ELSE_FALSE, is_file=True)
    # TODO implement a test that runs the sample step by step and checks
    # The false path is expected to be executed


def test_nested_structures():
    """Tests nested procedures and if statements."""
    interp = Interpreter()
    interp.read(NESTED_STRUCTURES, is_file=True)

    # Execute 'procedure a_test_procedure'
    interp.exec_next()
    # Execute 'if True'
    interp.exec_next()
    # Execute 'exec a_test_procedure'
    interp.exec_next()

    # Now we are inside 'a_test_procedure', at 'procedure nested_procedure'
    snapshot = Interpreter.Snapshot(interp)
    assert snapshot["Pointer"] == 1  # Inside a_test_procedure
    assert len(snapshot["Scope"]) == 2
    assert "a_test_procedure" in snapshot["Scope"][0]

    # Execute 'procedure nested_procedure'
    interp.exec_next()
    # Execute 'exec nested_procedure'
    interp.exec_next()

    # Now we are inside 'nested_procedure'
    snapshot = Interpreter.Snapshot(interp)
    assert (
        snapshot["Pointer"] == 2
    )  # Inside nested_procedure (at prnt 'Im defining a procedure here')
    assert len(snapshot["Scope"]) == 3
    assert "nested_procedure" in snapshot["Scope"][1]


def test_step_by_step_execution():
    """Tests step-by-step execution with exec_next."""
    interp = Interpreter()
    interp.read(ARITHMETIC_EXPRESSIONS, is_file=True)

    # Before any execution
    snapshot = Interpreter.Snapshot(interp)
    assert snapshot["Pointer"] == 0
    assert not snapshot["Scope"][0]

    # Execute first instruction: 5 + -10
    interp.exec_next()
    snapshot = Interpreter.Snapshot(interp)
    assert snapshot["Pointer"] == 1
    assert snapshot["Last result"] == -5

    # Execute second instruction: z = ((1+3) * 100) / 5
    interp.exec_next()
    snapshot = Interpreter.Snapshot(interp)
    assert snapshot["Pointer"] == 2
    assert snapshot["Scope"][0]["z"] == 80.0


def test_full_sample_final_state():
    """Tests the final state of the original complex sample.ns."""
    interp = Interpreter()
    interp.read(SAMPLE, is_file=True)

    try:
        while True:
            interp.exec_next()
    except EOF:
        pass

    snapshot = Interpreter.Snapshot(interp)
    scope = snapshot["Scope"][0]
    assert snapshot["Pointer"] == len(interp.memory.instr)
    assert scope["a"] == 1.0
    assert scope["b"] == 1
    assert scope["z"] == 1
    assert "x" not in scope


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        ("a=1;b=2;a++;b++", {"a": 2, "b": 3}),
    ],
)
def test_increment(source, expected):

    interp = Interpreter()
    interp.read(source)

    try:
        while interp.exec_next():
            pass
    except EOF:
        assert interp.scope() == expected


@pytest.mark.parametrize(
    ("source", "expected"),
    [("a=1;b=2;a--;b--", {"a": 0, "b": 1})],
)
def test_decrement(source, expected):
    interp = Interpreter()
    interp.read(source)

    try:
        while True:
            interp.exec_next()
    except EOF:
        assert interp.scope() == expected
