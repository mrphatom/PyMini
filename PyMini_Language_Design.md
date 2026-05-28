# PyMini Language Design

## 1. Introduction

PyMini is a lightweight, interpreted programming language designed for simplicity and readability. It features a clean syntax and provides a robust foundation for building logic-heavy applications and algorithmic prototypes.

## 2. Core Features

PyMini supports the following fundamental programming features:

*   **Variable Assignment:** Declare and assign values to variables.
*   **Basic Arithmetic Operations:** Perform addition, subtraction, multiplication, and division.
*   **Print Statement:** Output values to the console.
*   **Function Definitions:** Define reusable blocks of code with parameters and return values.
*   **Function Calls:** Execute defined functions.
*   **Conditional Statements:** Control program flow based on conditions (`if-else`).
*   **Looping Constructs:** Repeat blocks of code (`while` loops).
*   **Data Types:** Support for Integers, Strings, and Booleans.

## 3. Syntax Specification (BNF-like)

Below is a simplified Backus-Naur Form (BNF)-like specification for PyMini's syntax. Tokens are represented in uppercase, and keywords are enclosed in double quotes.

```bnf
program             ::= statement*

statement           ::= assignment_statement
                    | print_statement
                    | function_definition
                    | if_statement
                    | while_statement
                    | return_statement
                    | expression_statement

assignment_statement ::= "let" IDENTIFIER "=" expression ";"
print_statement     ::= "print" "(" expression ")" ";"

function_definition ::= "func" IDENTIFIER "(" (IDENTIFIER ("," IDENTIFIER)*)? ")" "{" statement* "}"
return_statement    ::= "return" expression ";"

if_statement        ::= "if" "(" expression ")" "{" statement* "}" ("else" "{" statement* "}")?
while_statement     ::= "while" "(" expression ")" "{" statement* "}"

expression_statement ::= expression ";"

expression          ::= equality
equality            ::= comparison (("==" | "!=") comparison)*
comparison          ::= term ((">" | ">=" | "<" | "<=") term)*
term                ::= factor (("+" | "-") factor)*
factor              ::= unary (("*" | "/") unary)*
unary               ::= ("!" | "-") unary | primary
primary             ::= NUMBER | STRING | "true" | "false" | "nil" | "(" expression ")" | IDENTIFIER | function_call

function_call       ::= IDENTIFIER "(" (expression ("," expression)*)? ")"
```

## 4. Semantics

*   **Variable Scope:** For simplicity, PyMini will initially support global scope for all variables. Future enhancements may include local and function-level scoping.
*   **Type System:** PyMini will be dynamically typed. Type checking will occur at runtime.
*   **Error Handling:** Runtime errors (e.g., type mismatches, undefined variables) will result in clear error messages.

## 5. Lexical Tokens

PyMini will recognize the following token types:

*   **Keywords:** `let`, `func`, `if`, `else`, `while`, `return`, `print`, `true`, `false`, `nil`
*   **Identifiers:** Sequences of letters, digits, and underscores, starting with a letter or underscore.
*   **Literals:**
    *   `NUMBER`: Integer literals (e.g., `123`, `0`).
    *   `STRING`: String literals enclosed in double quotes (e.g., `"hello"`).
*   **Operators:** `+`, `-`, `*`, `/`, `=`, `==`, `!=`, `>`, `>=`, `<`, `<=`, `!`
*   **Delimiters:** `(`, `)`, `{`, `}`, `;`, `,`
*   **Whitespace:** Ignored during lexical analysis.
*   **Comments:** Single-line comments starting with `//` will be ignored.

## 6. Future Enhancements (Out of Scope for Initial Version)

*   Local variable scoping
*   Classes and objects
*   Modules and imports
*   More complex data structures (lists, dictionaries)
*   Standard library functions
*   Error recovery during parsing
*   Optimizations
