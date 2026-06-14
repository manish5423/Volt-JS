# ThunderJS - A JavaScript Runtime in Python

ThunderJS is a custom JavaScript interpreter built from scratch in Python for the **THUNDER HACKATHON 2.0**. It aims to execute JavaScript code correctly by implementing a Lexer, a Recursive Descent Parser, and an AST-based Interpreter.

## Features Supported

- **Variables**: `let`, `const`, `var`.
- **Primitives**: `number`, `string`, `boolean`, `null`, `undefined`.
- **Operators**: Arithmetic (`+`, `-`, `*`, `/`, `%`, `**`), Comparison (`==`, `===`, `!=`, `!==`, `>`, `<`), Logical (`&&`, `||`, `!`).
- **Control Flow**: `if-else`, `for`, `while`, `do...while`.
- **Functions**: Declarations, Expressions, Arrow Functions, Callbacks.
- **Arrays**: Spread operator `[...]`, methods like `push`, `pop`, `join`, `reverse`, `map`, `filter`, `reduce`, `find`, `includes`, `indexOf`, `forEach`.
- **Strings**: `length`, `split`, `join`, `toUpperCase`, `toLowerCase`, `trim`, `substring`, `slice`, `replace`, `startsWith`, `endsWith`.
- **Built-in Objects**: `console.log`, `Math` (random, floor, ceil, round, etc.), `Date`.

## Project Structure

- `lexer.py`: Tokenizes the source code.
- `parser.py`: Generates an Abstract Syntax Tree (AST).
- `ast_nodes.py`: Defines the structure of the AST.
- `interpreter.py`: Evaluates the AST nodes.
- `environment.py`: Manages variable scoping and environments.
- `runtime.py`: Implements built-in JavaScript objects and methods.
- `main.py`: CLI entry point for running JS files.
- `examples/`: Contains the 5 test cases and additional examples.

## Getting Started

### Prerequisites

- Python 3.7+

### Installation

No external dependencies are required. Clone the repository and you are ready to go.

```bash
git clone <your-repo-link>
cd thundersssss
```

### Usage

To run a JavaScript file:

```bash
python main.py examples/odd_even.js
```

### Running Test Cases

The following test cases are provided in the `examples/` directory:

1. **Odd/Even Checker**: `python main.py examples/odd_even.js`
2. **Triangle Pattern**: `python main.py examples/triangle.js`
3. **Armstrong Number**: `python main.py examples/armstrong.js`
4. **Array Reverse**: `python main.py examples/reverse.js`
5. **Palindrome Check**: `python main.py examples/palindrome.js`

