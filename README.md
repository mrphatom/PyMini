# PyMini

PyMini is a lightweight, interpreted programming language implemented in Python. It is designed to be simple, readable, and expressive, featuring a syntax inspired by modern scripting languages.

## Features

- **Dynamic Typing:** No need to declare variable types.
- **First-Class Functions:** Define and pass functions with ease.
- **Control Flow:** Supports `if-else` conditionals and `while` loops.
- **Lexical Scoping:** Proper variable management within blocks and functions.
- **Clean Syntax:** Minimalist design with a focus on clarity.

## Installation

Ensure you have Python 3.x installed on your system. Clone this repository and you're ready to go.

```bash
git clone https://github.com/yourusername/pymini.git
cd pymini
```

## Usage

### Running a Script

You can execute PyMini source files (typically using the `.pymin` extension) by passing the file path to the interpreter:

```bash
python3 pymini.py examples/hello.pymin
```

### Interactive REPL

For quick testing and experimentation, you can launch the PyMini REPL:

```bash
python3 pymini.py
```

## Language Syntax

### Variables
Use the `let` keyword to declare variables:
```pymin
let x = 10;
let message = "Hello, World!";
```

### Functions
Functions are defined using the `func` keyword:
```pymin
func add(a, b) {
    return a + b;
}

print(add(5, 7)); // Outputs: 12
```

### Control Flow
```pymin
if (x > 5) {
    print("Greater");
} else {
    print("Smaller or equal");
}

let i = 0;
while (i < 3) {
    print(i);
    i = i + 1;
}
```

## Project Structure

- `pymini.py`: The core interpreter containing the lexer, parser, and tree-walk evaluator.
- `examples/`: A directory containing sample PyMini programs.
- `docs/`: Detailed documentation on language design and usage.
