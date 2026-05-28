# PyMini User Guide: Getting Started and Building Applications

PyMini is a powerful yet simple interpreted language. This guide will walk you through building your first application, understanding the syntax, and executing your code.

## 1. What Can You Build with PyMini?

PyMini is primarily an educational tool, but its feature set allows you to build several types of logic-heavy applications:

| Application Type | Description | PyMini Features Used |
| :--- | :--- | :--- |
| **Mathematical Calculators** | Create complex formulas for finance, physics, or geometry. | Arithmetic operators, variables, functions. |
| **Logic Engines** | Build decision-making tools or rule-based systems. | If-else statements, boolean logic, comparisons. |
| **Algorithm Prototypes** | Test recursive algorithms like Fibonacci or Factorials. | Functions, recursion, return statements. |
| **Text Processors** | Perform basic string concatenation and manipulation. | String literals, `+` operator for strings. |
| **Looping Automations** | Run repetitive tasks or simulations. | `while` loops, counters. |

## 2. How to Create a PyMini Program

To create a program, follow these three simple steps:

1.  **Open a Text Editor:** Use any standard text editor (like VS Code, Notepad, or even the terminal).
2.  **Write the Code:** Use the PyMini syntax (detailed in `language_design.md`).
3.  **Save the File:** Save your file with the `.pymin` extension (e.g., `my_app.pymin`).

### Example: A Simple Multiplier
```pymin
// Save this as multiply.pymin
let a = 12;
let b = 8;

func multiply(x, y) {
    return x * y;
}

let result = multiply(a, b);
print("The result of 12 * 8 is:");
print(result);
```

## 3. How to Execute and View Your Program

Since PyMini is built on Python, you use the Python interpreter to run the PyMini engine (`pymini.py`), which then executes your code.

### Method A: Running a File (Recommended)
Open your terminal or command prompt and run the following command:

```bash
python3 pymini.py your_filename.pymin
```

### Method B: Using the Interactive REPL
If you want to test code line-by-line, run the engine without a filename:

```bash
python3 pymini.py
```
This will open a prompt where you can type code directly:
```text
PyMini REPL (type 'exit' to quit)
> let x = 5;
> print(x * 2);
10
> exit
```

## 4. Key Syntax Reference

> **Variable Declaration:** Always use the `let` keyword.
> **Functions:** Defined using `func name(params) { ... }`.
> **Printing:** Use `print(value);` to output to the console.
> **Comments:** Use `//` for single-line notes.

## 5. Troubleshooting Common Issues

*   **Missing Semicolons:** Every statement must end with a `;`.
*   **Undefined Variables:** Ensure you define a variable with `let` before using it.
*   **Python Not Found:** Ensure Python 3 is installed and added to your system path.

---
**Author:** [Your Name]
**Date:** May 25, 2026
