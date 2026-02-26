import pytest

from src.exc import EOF
from src.interp import Interpreter
from src.lang.control import Def

# --- Constants for sample file paths ---
ASSIGNMENT_AND_PRINT = "tests/sample/assignment_and_print.ns"
PROCEDURE = "tests/sample/procedure.ns"
FUNCTION_WITH_RETURN = "tests/sample/function_with_return.ns"
ARITHMETIC_EXPRESSIONS = "tests/sample/arithmetic_expressions.ns"
IF_ELSE = "tests/sample/if_else.ns"
NESTED_STRUCTURES = "tests/sample/nested_structures.ns"
SAMPLE = "tests/sample/sample.ns"


def test_assignment_and_print():
    """Tests variable assignment and printing."""
    interpreter = Interpreter()
    interpreter.read(ASSIGNMENT_AND_PRINT, is_file=True)

    try:
        while True:
            interpreter.exec_next()
    except EOF:
        pass

    snapshot = Interpreter.Snapshot(interpreter)
    assert snapshot["Pointer"] == len(interpreter.memory.instr)
    assert snapshot["Scope"][0]["who"] == "World"
    assert snapshot["Instruction"] is None
    assert snapshot["Last result"] is None
    assert len(snapshot["Block stack"]) == 1
    assert snapshot["Stack"] == []
    assert snapshot["Ctrl stack"] == [True]


def test_procedure():
    """Tests a simple procedure definition and execution."""
    interpreter = Interpreter()
    interpreter.read(PROCEDURE, is_file=True)

    # Before 'exec test'
    interpreter.exec_next()  # 'procedure test'
    snapshot = Interpreter.Snapshot(interpreter)
    assert snapshot["Pointer"] == 5  # After defining the procedure, pointer moves to 'exec test'
    assert "test" in snapshot["Scope"][0]

    # Execute 'exec test'
    interpreter.exec_next()
    snapshot = Interpreter.Snapshot(interpreter)

    # Inside the procedure, at the first 'prnt 9'
    assert snapshot["Pointer"] == 1  # Pointer is at the first instruction *inside* the procedure (prnt 9)
    assert len(snapshot["Scope"]) == 2
    #assert snapshot["Block stack"] == ["<main>", snapshot["Scope"][1]["test"]]
    assert snapshot["Stack"] == [{"ret_addr": 5}]


def test_function_with_return():
    """Tests a function with parameters and a return value."""
    interpreter = Interpreter()
    interpreter.read(FUNCTION_WITH_RETURN, is_file=True)

    try:
        while True:
            interpreter.exec_next()
    except EOF:
        pass

    snapshot = Interpreter.Snapshot(interpreter)
    assert snapshot["Pointer"] == len(interpreter.memory.instr)
    assert snapshot["Scope"][0]["r"] == 6
    assert isinstance(snapshot["Scope"][0]["func"], Def)
    assert snapshot["Instruction"] is None
    assert snapshot["Last result"] is None


def test_arithmetic_expressions():
    """Tests simple and complex arithmetic expressions."""
    interpreter = Interpreter()
    interpreter.read(ARITHMETIC_EXPRESSIONS, is_file=True)

    try:
        while True:
            interpreter.exec_next()
    except EOF:
        pass

    snapshot = Interpreter.Snapshot(interpreter)
    assert snapshot["Pointer"] == len(interpreter.memory.instr)
    assert snapshot["Scope"][0]["z"] == 80.0
    assert snapshot["Instruction"] is None
    assert snapshot["Last result"] is None


def test_if_else():
    """Tests a basic if/else control flow example."""
    interpreter = Interpreter()
    interpreter.read(IF_ELSE, is_file=True)

    try:
        while True:
            interpreter.exec_next()
    except EOF:
        pass

    snapshot = Interpreter.Snapshot(interpreter)
    scope = snapshot["Scope"][0]
    assert scope["a"] == 1
    assert scope["b"] == 2
    assert snapshot["Instruction"] is None


def test_if_else_step_by_step():
    """Tests a basic if/else control flow example."""
    interpreter = Interpreter()
    interpreter.read(IF_ELSE, is_file=True)

    try:
        while True:
            interpreter.exec_next()
    except EOF:
        pass

    snapshot = Interpreter.Snapshot(interpreter)
    scope = snapshot["Scope"][0]
    assert scope["a"] == 1
    assert scope["b"] == 2
    assert snapshot["Instruction"] is None


def test_nested_structures():
    """Tests nested procedures and if statements."""
    interpreter = Interpreter()
    interpreter.read(NESTED_STRUCTURES, is_file=True)

    # Execute 'procedure a_test_procedure'
    interpreter.exec_next()
    # Execute 'if True'
    interpreter.exec_next()
    # Execute 'exec a_test_procedure'
    interpreter.exec_next()

    # Now we are inside 'a_test_procedure', at 'procedure nested_procedure'
    snapshot = Interpreter.Snapshot(interpreter)
    assert snapshot["Pointer"] == 1  # Inside a_test_procedure
    assert len(snapshot["Scope"]) == 2
    assert "a_test_procedure" in snapshot["Scope"][0]

    # Execute 'procedure nested_procedure'
    interpreter.exec_next()
    # Execute 'exec nested_procedure'
    interpreter.exec_next()

    # Now we are inside 'nested_procedure'
    snapshot = Interpreter.Snapshot(interpreter)
    assert snapshot["Pointer"] == 2  # Inside nested_procedure (at prnt 'Im defining a procedure here')
    assert len(snapshot["Scope"]) == 3
    assert "nested_procedure" in snapshot["Scope"][1]


def test_step_by_step_execution():
    """Tests step-by-step execution with exec_next."""
    interpreter = Interpreter()
    interpreter.read(ARITHMETIC_EXPRESSIONS, is_file=True)

    # Before any execution
    snapshot = Interpreter.Snapshot(interpreter)
    assert snapshot["Pointer"] == 0
    assert not snapshot["Scope"][0]

    # Execute first instruction: 5 + -10
    interpreter.exec_next()
    snapshot = Interpreter.Snapshot(interpreter)
    assert snapshot["Pointer"] == 1
    assert snapshot["Last result"] == -5

    # Execute second instruction: z = ((1+3) * 100) / 5
    interpreter.exec_next()
    snapshot = Interpreter.Snapshot(interpreter)
    assert snapshot["Pointer"] == 2
    assert snapshot["Scope"][0]["z"] == 80.0


def test_full_sample_final_state():
    """Tests the final state of the original complex sample.ns."""
    interpreter = Interpreter()
    interpreter.read(SAMPLE, is_file=True)

    try:
        while True:
            interpreter.exec_next()
    except EOF:
        pass

    snapshot = Interpreter.Snapshot(interpreter)
    scope = snapshot["Scope"][0]
    assert snapshot["Pointer"] == len(interpreter.memory.instr)
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

    interpreter = Interpreter()
    interpreter.read(source)

    try:
        while interpreter.exec_next():
            pass
    except EOF:
        assert interpreter.scope() == expected


@pytest.mark.parametrize(
    ("source", "expected"),
    [("a=1;b=2;a--;b--", {"a": 0, "b": 1})],
)
def test_decrement(source, expected):
    interpreter = Interpreter()
    interpreter.read(source)

    try:
        while True:
            interpreter.exec_next()
    except EOF:
        assert interpreter.scope() == expected
