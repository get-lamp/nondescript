import pytest
from src.interp import Interpreter
from src.parser import Parser
from src.lang import Lang
from io import BytesIO # Needed for Lexer if it uses BytesIO directly

# This fixture now correctly passes the raw source string to Interpreter
# It assumes Interpreter's __init__ will handle internal parsing.
@pytest.fixture
def interpreter_and_program():
    with open("tests/sample/sample.ns") as f:
        source = f.read()
    
    # Instantiate Interpreter with the raw source string.
    interp = Interpreter(source)
    
    # Also, explicitly parse the source to get the AST for feeding to eval().
    # This assumes Interpreter does not expose its internal parsed program directly.
    parser = Parser(Lang, source)
    program_ast = parser.parse()
    
    return interp, program_ast

def test_complex_assign(interpreter_and_program):
    interp, program = interpreter_and_program
    # Corresponds to the state at Pointer 14 in output.txt
    while interp.pntr < 14:
        instruction = program[interp.pntr]
        interp.eval(instruction)

    # State after executing instruction at pointer 13, before 14
    snapshot = interp.snapshot()
    assert snapshot.pointer == 14
    assert 'z' not in snapshot.scope[0] # 'z' should not be in scope yet

    # Now, execute the assignment at pointer 14 and check the state after
    instruction_at_14 = program[interp.pntr]
    interp.eval(instruction_at_14) # Execute the assignment
    snapshot = interp.snapshot()
    assert snapshot.pointer == 15 # Pointer should advance after eval
    assert snapshot.scope[0]['z'] == 80.0
    assert snapshot.last_result.word == 'z' # Assuming last_result stores the identifier for assignment

def test_procedure_call_and_scope(interpreter_and_program):
    interp, program = interpreter_and_program
    # Corresponds to the state at Pointer 6, before calling 'test'
    while interp.pntr < 6:
        instruction = program[interp.pntr]
        interp.eval(instruction)

    # State before executing 'exec test' at pointer 6
    snapshot = interp.snapshot()
    assert snapshot.pointer == 6
    assert len(snapshot.scope) == 1
    assert 'test' in snapshot.scope[0]
    
    # Execute 'exec test' (instruction at pointer 6)
    instruction_at_6 = program[interp.pntr]
    interp.eval(instruction_at_6)
    
    # State after entering procedure 'test', at Pointer 2 (as per output.txt)
    snapshot = interp.snapshot()
    assert snapshot.pointer == 2 # This is the entry point of the procedure
    assert len(snapshot.scope) == 2  # New scope for the procedure
    assert snapshot.block_stack == ['<main>', '<keyword procedure>']
    assert len(snapshot.stack) == 1
    assert snapshot.stack[0]['ret_addr'] == 6

def test_nested_procedure_call(interpreter_and_program):
    interp, program = interpreter_and_program
    # Run up to the point where 'nested_procedure' is about to be executed (Pointer 32)
    while interp.pntr < 32:
        instruction = program[interp.pntr]
        interp.eval(instruction)

    snapshot = interp.snapshot()
    assert snapshot.pointer == 32
    assert snapshot.block_stack == ['<main>', '<keyword if>', '<keyword procedure>']

    # Execute 'exec nested_procedure' (instruction at pointer 32)
    instruction_at_32 = program[interp.pntr]
    interp.eval(instruction_at_32)
    
    # State after entering 'nested_procedure', at Pointer 17 (as per output.txt)
    snapshot = interp.snapshot()
    assert snapshot.pointer == 17
    assert len(snapshot.scope) == 3 # main, a_test_procedure, nested_procedure
    assert snapshot.block_stack == ['<main>', '<keyword if>', '<keyword procedure>', '<keyword procedure>']
    assert len(snapshot.stack) == 2
    assert snapshot.stack[1]['ret_addr'] == 32

def test_if_else_logic(interpreter_and_program):
    interp, program = interpreter_and_program
    # Run up to the 'if j == 2' check (Pointer 26)
    while interp.pntr < 26:
        instruction = program[interp.pntr]
        interp.eval(instruction)

    snapshot = interp.snapshot()
    # Assuming 'j' is in the second scope (procedure scope)
    assert snapshot.scope[1]['j'] == 2

    # Execute 'if j == 2' (instruction at pointer 26)
    instruction_at_26 = program[interp.pntr]
    interp.eval(instruction_at_26)
    snapshot = interp.snapshot()
    assert snapshot.pointer == 27
    assert snapshot.ctrl_stack == [True, True, True] # Assuming the 'if' condition is true

    # Execute 'prnt j' (instruction at pointer 27)
    instruction_at_27 = program[interp.pntr]
    interp.eval(instruction_at_27)

    # Execute 'else' (instruction at pointer 28)
    # The 'else' instruction would be skipped if 'if' was true, but eval() might still be called.
    # The ctrl_stack determines if instructions within the 'else' block are executed.
    instruction_at_28 = program[interp.pntr]
    interp.eval(instruction_at_28) # This eval might just update ctrl_stack

    snapshot = interp.snapshot()
    assert snapshot.pointer == 29 # Should advance past 'else'
    # If the 'if' was true, the 'else' block should be disabled, making ctrl_stack's last element False
    assert snapshot.ctrl_stack == [True, True, False]

def test_final_state(interpreter_and_program):
    interp, program = interpreter_and_program
    # Run the entire program manually by repeatedly calling eval
    # The last pointer in output.txt is 56. We'll run until it's beyond the program length.
    program_length = len(program)
    while interp.pntr < program_length:
        instruction = program[interp.pntr]
        interp.eval(instruction)

    snapshot = interp.snapshot()

    # Check some final values in the global scope (index 0)
    assert snapshot.scope[0]['a'] == 1.0
    assert snapshot.scope[0]['b'] == 1
    # 'z' was updated inside the if block, which was true.
    assert snapshot.scope[0]['z'] == 1 # This might be 80.0 if the 'if' was for the outer block.
                                       # From output.txt, z is 80.0 at Pointer 15, then 1 at Pointer 47.
                                       # So final 'z' should be 1.
    assert 'x' not in snapshot.scope[0] # 'x' was set in the 'else' block, which should be skipped.