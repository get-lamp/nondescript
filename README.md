# NonDeScript
Yet another tiny language

## Usage

Running from source code

```pipenv run python run.py <filename>```

It outputs debugging info to a `.debug` file.

There is some sample source at `tests/sample`

## Running tests

```pipenv run pytest .```

## Language Overview

NonDeScript is a simple, dynamic, and imperative scripting language. It supports common programming constructs such as variable assignments, arithmetic operations, control flow structures (if/else), and procedures/functions. The syntax is designed to be straightforward and underwhelming.

### Implementation Details

The interpreter and its components are built from scratch, providing a clear example of language implementation concepts.

*   **Lexer**: The lexer (or scanner) is a hand-rolled implementation. It performs tokenization by scanning the raw source code character by character, mapping sequences of characters to tokens based on a predefined set of keywords, operators, and delimiters defined within the language's grammar.

*   **Grammar**: The language's grammar is defined programmatically within the source code itself, acting as an internal Domain-Specific Language (DSL). Instead of using external grammar definition files (like BNF or EBNF), the valid syntax, keywords, and operator precedence are specified directly in Python classes and data structures.

*   **Parser**: The parser uses a **Recursive Descent** approach. It processes the stream of tokens from the lexer to build an Abstract Syntax Tree (AST). The parsing logic includes an implementation of an operator-precedence parser to correctly handle mathematical expressions and their order of operations.

*   **Interpreter**: The interpreter is a **tree-walking interpreter**. After the parser generates the AST, the interpreter traverses this tree, evaluating and executing each node directly. It manages program state, including memory, scope, and the call stack, as it walks the tree. It does not compile the code to bytecode or machine code.
