import pytest

from src.exc import EOF
from src.interp import Interpreter
from src.lang.control import Def, Main

# --- Constants for sample file paths ---
ASSIGNMENT_AND_PRINT = "tests/sample/assignment_and_print.ns"
PROCEDURE = "tests/sample/procedure.ns"
FUNCTION_WITH_RETURN = "tests/sample/function_with_return.ns"
FIBONACCI = "tests/sample/fibonacci.ns"
ARITHMETIC_EXPRESSIONS = "tests/sample/arithmetic_expressions.ns"
IF_ELSE_TRUE = "tests/sample/if_else_true.ns"
IF_ELSE_FALSE = "tests/sample/if_else_false.ns"
NESTED_STRUCTURES = "tests/sample/nested_structures.ns"
FOR_LOOP = "tests/sample/for_loop.ns"
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

    assert interp.instr_pointer == len(interp.memory.instr)
    assert interp.memory.scope[0]["who"] == "World"
    assert (
        interp.memory.instr[interp.instr_pointer]
        if interp.instr_pointer < len(interp.memory.instr)
        else None
    ) is None
    assert interp.last is None
    assert len(interp.block_stack) == 1
    assert interp.memory.stack == []
    assert interp.ctrl_stack == [True]


def test_procedure():
    """Tests a simple procedure definition and execution."""
    interp = Interpreter()
    interp.read(PROCEDURE, is_file=True)
    assert interp.instr_pointer == 0
    assert isinstance(interp.block_stack[-1], Main)
    assert interp.ctrl_stack == [True]

    # Before 'exec test'
    interp.exec_next()  # 'procedure test'

    assert (
        interp.instr_pointer == 5
    )  # After defining the procedure, pointer moves to 'exec test'
    assert "test" in interp.memory.scope[0]

    # Execute 'exec test'
    interp.exec_next()

    # Inside the procedure, at the first 'prnt 9'
    assert (
        interp.instr_pointer == 1
    )  # Pointer is at the first instruction *inside* the procedure (prnt 9)
    assert len(interp.memory.scope) == 2
    # assert interp.block_stack == ["<main>", interp.memory.scope[1]["test"]]
    assert interp.memory.stack == [{"ret_addr": 5}]


def test_function_with_return():
    """Tests a function with parameters and a return value."""
    interp = Interpreter()
    interp.read(FUNCTION_WITH_RETURN, is_file=True)

    try:
        while True:
            interp.exec_next()
    except EOF:
        pass

    assert interp.instr_pointer == len(interp.memory.instr)
    assert interp.memory.scope[0]["r"] == 6
    assert isinstance(interp.memory.scope[0]["func"], Def)
    assert (
        interp.memory.instr[interp.instr_pointer]
        if interp.instr_pointer < len(interp.memory.instr)
        else None
    ) is None
    assert interp.last is None


def test_function_fibonacci():
    """Tests a function with parameters and a return value."""
    interp = Interpreter()
    interp.read(FIBONACCI, is_file=True)

    try:
        while True:
            interp.exec_next()
    except EOF:
        pass


def test_arithmetic_expressions():
    """Tests simple and complex arithmetic expressions."""
    interp = Interpreter()
    interp.read(ARITHMETIC_EXPRESSIONS, is_file=True)

    try:
        while True:
            interp.exec_next()
    except EOF:
        pass

    assert interp.instr_pointer == len(interp.memory.instr)
    assert interp.memory.scope[0]["z"] == 80.0
    assert (
        interp.memory.instr[interp.instr_pointer]
        if interp.instr_pointer < len(interp.memory.instr)
        else None
    ) is None
    assert interp.last is None


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
    assert interp.instr_pointer == 1  # Inside a_test_procedure
    assert len(interp.memory.scope) == 2
    assert "a_test_procedure" in interp.memory.scope[0]

    # Execute 'procedure nested_procedure'
    interp.exec_next()
    # Execute 'exec nested_procedure'
    interp.exec_next()

    # Now we are inside 'nested_procedure'
    assert (
        interp.instr_pointer == 2
    )  # Inside nested_procedure (at prnt 'Im defining a procedure here')
    assert len(interp.memory.scope) == 3
    assert "nested_procedure" in interp.memory.scope[1]


def test_step_by_step_execution():
    """Tests step-by-step execution with exec_next."""
    interp = Interpreter()
    interp.read(ARITHMETIC_EXPRESSIONS, is_file=True)

    # Before any execution
    assert interp.instr_pointer == 0
    assert not interp.memory.scope[0]

    # Execute first instruction: 5 + -10
    interp.exec_next()
    assert interp.instr_pointer == 1
    assert interp.last == -5

    # Execute second instruction: z = ((1+3) * 100) / 5
    interp.exec_next()
    assert interp.instr_pointer == 2
    assert interp.memory.scope[0]["z"] == 80.0


def test_full_sample_final_state():
    """Tests the final state of the original complex sample.ns."""
    interp = Interpreter()
    interp.read(SAMPLE, is_file=True)

    try:
        while True:
            interp.exec_next()
    except EOF:
        pass

    scope = interp.memory.scope[0]
    assert interp.instr_pointer == len(interp.memory.instr)
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


def test_for_loop_false_condition():
    source = """
        x = 0
        for i=0; i<0; i++
            x = 1
        end
    """
    interp = Interpreter()
    interp.read(source)
    try:
        while True:
            interp.exec_next()
    except EOF:
        pass
    assert interp.scope()["i"] == 0
    assert interp.scope()["x"] == 0


def test_for_loop_10_iterations():
    source = """
    for i=0; i<10; i++
        prnt i
    end
    """
    interp = Interpreter()
    interp.read(source)
    try:
        while True:
            interp.exec_next()
    except EOF:
        pass
    assert interp.scope()["i"] == 10


def test_nested_for_loops():
    source = """
    z=0
    for x=0; x < 2; x++
        prnt x
        for y=0; y < 2; y++
            z++
            prnt y, z
        end
    end
    """
    interp = Interpreter()
    interp.read(source)
    try:
        while True:
            interp.exec_next()
    except EOF:
        pass
    assert interp.scope()["x"] == 2
    assert interp.scope()["y"] == 2
    assert interp.scope()["z"] == 4
