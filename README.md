# PyMini

PyMini is a lightweight, interpreted programming language implemented in Python. It is designed to be simple, readable, and expressive, featuring a syntax inspired by modern scripting languages.

## Features

- **Dynamic Typing:** No need to declare variable types.
- **First-Class Functions:** Define and pass functions with ease.
- **Control Flow:** Supports `if-else` conditionals, `while` loops, and logical operators (`and`, `or`).
- **Arithmetic:** Full support for `+`, `-`, `*`, `/`, and `%` (modulo).
- **Built-in Functions:** Native functions like `clock()`, `len()`, and Web3 helpers.
- **Rust Core (PyO3):** High-performance Solana-facing logic implemented in Rust.
- **Web3 Features:** Direct Solana RPC integration and Borsh deserialization.
- **Lexical Scoping:** Proper variable management within blocks and functions.
- **Clean Syntax:** Minimalist design with a focus on clarity.

## Installation

Ensure you have Python 3.x and Rust installed on your system. 

1. Clone the repository:
```bash
git clone https://github.com/mrphatom/PyMini.git
cd PyMini
```

2. Build and install the Rust core:
```bash
cd pymini_core
maturin build --release
pip install target/wheels/*.whl
cd ..
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

### Web3 (Solana)
PyMini now supports Solana operations via its Rust core:
```pymin
let rpc = "https://api.mainnet-beta.solana.com";
let addr = "11111111111111111111111111111111";
let balance = solana_get_balance(rpc, addr);
print(balance);
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
