from src.interp import Interpreter

# --- Constants for sample file paths ---
ASSIGNMENT_AND_PRINT = "tests/sample/assignment_and_print.ns"
PROCEDURE = "tests/sample/procedure.ns"
FUNCTION_WITH_RETURN = "tests/sample/function_with_return.ns"
ARITHMETIC_EXPRESSIONS = "tests/sample/arithmetic_expressions.ns"
IF_ELSE = "tests/sample/if_else.ns"
NESTED_STRUCTURES = "tests/sample/nested_structures.ns"
SAMPLE = "tests/sample/sample.ns"


def _run_test(filepath):
    """Helper function to run a script to completion and return the interpreter."""

    interpreter = Interpreter()
    interpreter.read(filepath, is_file=True)

    while interpreter.exec_next() is not False:
        pass

    return interpreter


def test_assignment_and_print():
    """Tests variable assignment and printing."""

    interpreter = _run_test(ASSIGNMENT_AND_PRINT)
    snapshot = Interpreter.Snapshot(interpreter)

    assert snapshot["Scope"][0]["who"] == "World"


def test_procedure():
    """Tests a simple procedure definition and execution."""

    _run_test(PROCEDURE)


def test_function_with_return():
    """Tests a function with parameters and a return value."""

    interpreter = _run_test(FUNCTION_WITH_RETURN)
    snapshot = Interpreter.Snapshot(interpreter)

    assert snapshot["Scope"][0]["r"] == 6


def test_arithmetic_expressions():
    """Tests simple and complex arithmetic expressions."""

    interpreter = _run_test(ARITHMETIC_EXPRESSIONS)
    snapshot = Interpreter.Snapshot(interpreter)

    assert snapshot["Scope"][0]["z"] == 80.0


def test_if_else():
    """Tests a basic if/else control flow example."""

    _run_test(IF_ELSE)


def test_nested_structures():
    """Tests nested procedures and if statements."""

    _run_test(NESTED_STRUCTURES)


def test_step_by_step_execution():
    """Tests step-by-step execution with exec_next."""

    interpreter = Interpreter()
    interpreter.read(ARITHMETIC_EXPRESSIONS, is_file=True)

    # Before any execution
    snapshot = Interpreter.Snapshot(interpreter)

    assert snapshot["Pointer"] == 0
    assert not snapshot["Scope"][0]  # Scope should be empty

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
    assert snapshot["Last result"].word == "z"


def test_full_sample_final_state():
    """Tests the final state of the original complex sample.ns."""

    interpreter = _run_test(SAMPLE)
    snapshot = Interpreter.Snapshot(interpreter)

    scope = snapshot["Scope"][0]

    assert scope["a"] == 1.0
    assert scope["b"] == 1
    assert scope["z"] == 1
    assert "x" not in scope
