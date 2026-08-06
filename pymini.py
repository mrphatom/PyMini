import sys

# --- Token Types ---
class TokenType:
    # Keywords
    LET = 'LET'
    FUNC = 'FUNC'
    IF = 'IF'
    ELSE = 'ELSE'
    WHILE = 'WHILE'
    FOR = 'FOR'
    TRY = 'TRY'
    CATCH = 'CATCH'
    RETURN = 'RETURN'
    PRINT = 'PRINT'
    TRUE = 'TRUE'
    FALSE = 'FALSE'
    NIL = 'NIL'
    NULL = 'NULL'

    # Operators
    PLUS = 'PLUS'
    MINUS = 'MINUS'
    STAR = 'STAR'
    SLASH = 'SLASH'
    EQ = 'EQ'
    EQ_EQ = 'EQ_EQ'
    AND = 'AND'
    OR = 'OR'
    IN = 'IN'
    MODULO = 'MODULO'
    BANG = 'BANG'
    BANG_EQ = 'BANG_EQ'
    GT = 'GT'
    GE = 'GE'
    LT = 'LT'
    LE = 'LE'

    # Delimiters
    LPAREN = 'LPAREN'
    RPAREN = 'RPAREN'
    LBRACE = 'LBRACE'
    RBRACE = 'RBRACE'
    LBRACKET = 'LBRACKET'
    RBRACKET = 'RBRACKET'
    SEMICOLON = 'SEMICOLON'
    COMMA = 'COMMA'
    COLON = 'COLON'

    # Literals
    IDENTIFIER = 'IDENTIFIER'
    STRING = 'STRING'
    NUMBER = 'NUMBER'

    EOF = 'EOF'

# --- Token Class ---
class Token:
    def __init__(self, type, lexeme, literal, line):
        self.type = type
        self.lexeme = lexeme
        self.literal = literal
        self.line = line

    def __str__(self):
        return f'{self.type} {self.lexeme} {self.literal}'

# --- Lexer Class ---
class Lexer:
    def __init__(self, source):
        self.source = source
        self.tokens = []
        self.start = 0
        self.current = 0
        self.line = 1

    def scan_tokens(self):
        while not self.is_at_end():
            self.start = self.current
            self.scan_token()
        self.tokens.append(Token(TokenType.EOF, '', None, self.line))
        return self.tokens

    def is_at_end(self):
        return self.current >= len(self.source)

    def advance(self):
        char = self.source[self.current]
        self.current += 1
        return char

    def add_token(self, type, literal=None):
        text = self.source[self.start:self.current]
        self.tokens.append(Token(type, text, literal, self.line))

    def match(self, expected):
        if self.is_at_end():
            return False
        if self.source[self.current] != expected:
            return False
        self.current += 1
        return True

    def peek(self):
        if self.is_at_end():
            return '\0'
        return self.source[self.current]

    def peek_next(self):
        if self.current + 1 >= len(self.source):
            return '\0'
        return self.source[self.current + 1]

    def string(self):
        while self.peek() != '"' and not self.is_at_end():
            if self.peek() == '\n':
                self.line += 1
            self.advance()
        if self.is_at_end():
            # Error: Unterminated string
            return
        self.advance() # The closing "
        value = self.source[self.start + 1:self.current - 1]
        self.add_token(TokenType.STRING, value)

    def number(self):
        while self.peek().isdigit():
            self.advance()
        self.add_token(TokenType.NUMBER, int(self.source[self.start:self.current]))

    def identifier(self):
        while self.peek().isalnum() or self.peek() == '_':
            self.advance()
        text = self.source[self.start:self.current]
        # Check for keywords
        keyword_type = self.keywords.get(text)
        if keyword_type:
            self.add_token(keyword_type)
        else:
            self.add_token(TokenType.IDENTIFIER)

    keywords = {
        'let': TokenType.LET,
        'func': TokenType.FUNC,
        'if': TokenType.IF,
        'else': TokenType.ELSE,
        'while': TokenType.WHILE,
        'for': TokenType.FOR,
        'try': TokenType.TRY,
        'catch': TokenType.CATCH,
        'return': TokenType.RETURN,
        'print': TokenType.PRINT,
        'true': TokenType.TRUE,
        'false': TokenType.FALSE,
        'nil': TokenType.NIL,
        'null': TokenType.NULL,
        'and': TokenType.AND,
        'or': TokenType.OR,
        'in': TokenType.IN,
    }

    def scan_token(self):
        char = self.advance()
        if char == '(':
            self.add_token(TokenType.LPAREN)
        elif char == ')':
            self.add_token(TokenType.RPAREN)
        elif char == '{':
            self.add_token(TokenType.LBRACE)
        elif char == '}':
            self.add_token(TokenType.RBRACE)
        elif char == '[':
            self.add_token(TokenType.LBRACKET)
        elif char == ']':
            self.add_token(TokenType.RBRACKET)
        elif char == ";":
            self.add_token(TokenType.SEMICOLON)
        elif char == ",":
            self.add_token(TokenType.COMMA)
        elif char == ":":
            self.add_token(TokenType.COLON)
        elif char == "%":
            self.add_token(TokenType.MODULO)
        elif char == '#':
            while self.peek() != '\n' and not self.is_at_end():
                self.advance()
        elif char == '+':
            self.add_token(TokenType.PLUS)
        elif char == '-':
            self.add_token(TokenType.MINUS)
        elif char == '*':
            self.add_token(TokenType.STAR)
        elif char == '/':
            if self.match('/'): # Handle single-line comments
                while self.peek() != '\n' and not self.is_at_end():
                    self.advance()
            else:
                self.add_token(TokenType.SLASH)
        elif char == '!':
            self.add_token(TokenType.BANG_EQ if self.match('=') else TokenType.BANG)
        elif char == '=':
            self.add_token(TokenType.EQ_EQ if self.match('=') else TokenType.EQ)
        elif char == '<':
            self.add_token(TokenType.LE if self.match('=') else TokenType.LT)
        elif char == '>':
            self.add_token(TokenType.GE if self.match('=') else TokenType.GT)
        elif char == ' ' or char == '\r' or char == '\t':
            pass # Ignore whitespace
        elif char == '\n':
            self.line += 1
        elif char == '"':
            self.string()
        elif char.isdigit():
            self.number()
        elif char.isalpha() or char == '_':
            self.identifier()
        else:
            # Error: Unexpected character
            pass

# --- AST Node Definitions ---
class Expr: pass

class Binary(Expr):
    def __init__(self, left, operator, right):
        self.left = left
        self.operator = operator
        self.right = right

class Unary(Expr):
    def __init__(self, operator, right):
        self.operator = operator
        self.right = right

class Literal(Expr):
    def __init__(self, value):
        self.value = value

class List(Expr):
    def __init__(self, elements):
        self.elements = elements

class GetIndex(Expr):
    def __init__(self, callee, index):
        self.callee = callee
        self.index = index

class SetIndex(Expr):
    def __init__(self, callee, index, value):
        self.callee = callee
        self.index = index
        self.value = value

class Dict(Expr):
    def __init__(self, entries):
        self.entries = entries

class Grouping(Expr):
    def __init__(self, expression):
        self.expression = expression

class Variable(Expr):
    def __init__(self, name):
        self.name = name

class Assign(Expr):
    def __init__(self, name, value):
        self.name = name
        self.value = value

class Call(Expr):
    def __init__(self, callee, paren, arguments):
        self.callee = callee
        self.paren = paren
        self.arguments = arguments

class Stmt: pass

class Expression(Stmt):
    def __init__(self, expression):
        self.expression = expression

class Print(Stmt):
    def __init__(self, expression):
        self.expression = expression

class Var(Stmt):
    def __init__(self, name, initializer):
        self.name = name
        self.initializer = initializer

class Block(Stmt):
    def __init__(self, statements):
        self.statements = statements

class If(Stmt):
    def __init__(self, condition, then_branch, else_branch):
        self.condition = condition
        self.then_branch = then_branch
        self.else_branch = else_branch

class While(Stmt):
    def __init__(self, condition, body):
        self.condition = condition
        self.body = body

class ForIn(Stmt):
    def __init__(self, item, iterable, body):
        self.item = item
        self.iterable = iterable
        self.body = body

class Function(Stmt):
    def __init__(self, name, params, body):
        self.name = name
        self.params = params
        self.body = body

class Return(Stmt):
    def __init__(self, keyword, value):
        self.keyword = keyword
        self.value = value

class TryCatch(Stmt):
    def __init__(self, try_block, catch_var, catch_block):
        self.try_block = try_block
        self.catch_var = catch_var
        self.catch_block = catch_block

# --- Parser Class ---
class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.current = 0

    def parse(self):
        statements = []
        while not self.is_at_end():
            statements.append(self.declaration())
        return statements

    def declaration(self):
        try:
            if self.match(TokenType.LET): return self.var_declaration()
            if self.match(TokenType.FUNC): return self.function_declaration()
            return self.statement()
        except Exception as e:
            print(f"Parse Error: {e}")
            self.synchronize()
            return None

    def function_declaration(self):
        name = self.consume(TokenType.IDENTIFIER, "Expect function name.")
        self.consume(TokenType.LPAREN, "Expect '(' after function name.")
        parameters = []
        if not self.check(TokenType.RPAREN):
            while True:
                parameters.append(self.consume(TokenType.IDENTIFIER, "Expect parameter name."))
                if not self.match(TokenType.COMMA): break
        self.consume(TokenType.RPAREN, "Expect ')' after parameters.")
        self.consume(TokenType.LBRACE, "Expect '{' before function body.")
        body = self.block()
        return Function(name, parameters, body)

    def var_declaration(self):
        name = self.consume(TokenType.IDENTIFIER, "Expect variable name.")
        initializer = None
        if self.match(TokenType.EQ):
            initializer = self.expression()
        self.consume(TokenType.SEMICOLON, "Expect ';' after variable declaration.")
        return Var(name, initializer)

    def statement(self):
        if self.match(TokenType.IF): return self.if_statement()
        if self.match(TokenType.PRINT): return self.print_statement()
        if self.match(TokenType.RETURN): return self.return_statement()
        if self.match(TokenType.WHILE): return self.while_statement()
        if self.match(TokenType.FOR): return self.for_statement()
        if self.match(TokenType.TRY): return self.try_statement()
        if self.match(TokenType.LBRACE): return Block(self.block())
        return self.expression_statement()

    def for_statement(self):
        if self.match(TokenType.LPAREN):
            # C-style for loop
            initializer = None
            if self.match(TokenType.SEMICOLON):
                initializer = None
            elif self.match(TokenType.LET):
                initializer = self.var_declaration()
            else:
                initializer = self.expression_statement()
                
            condition = None
            if not self.check(TokenType.SEMICOLON):
                condition = self.expression()
            self.consume(TokenType.SEMICOLON, "Expect ';' after loop condition.")
            
            increment = None
            if not self.check(TokenType.RPAREN):
                increment = self.expression()
            self.consume(TokenType.RPAREN, "Expect ')' after for clauses.")
            
            body = self.statement()
            
            if increment is not None:
                body = Block([body, Expression(increment)])
                
            if condition is None:
                condition = Literal(True)
            body = While(condition, body)
            
            if initializer is not None:
                body = Block([initializer, body])
                
            return body
        else:
            # for-in iterator loop
            item = self.consume(TokenType.IDENTIFIER, "Expect variable name after 'for'.")
            self.consume(TokenType.IN, "Expect 'in' after variable name.")
            iterable = self.expression()
            body = self.statement()
            return ForIn(item, iterable, body)

    def try_statement(self):
        self.consume(TokenType.LBRACE, "Expect '{' after 'try'.")
        try_block = self.block()
        self.consume(TokenType.CATCH, "Expect 'catch' after try block.")
        self.consume(TokenType.LPAREN, "Expect '(' after 'catch'.")
        catch_var = self.consume(TokenType.IDENTIFIER, "Expect error variable name.")
        self.consume(TokenType.RPAREN, "Expect ')' after error variable.")
        self.consume(TokenType.LBRACE, "Expect '{' before catch body.")
        catch_block = self.block()
        return TryCatch(try_block, catch_var, catch_block)

    def if_statement(self):
        self.consume(TokenType.LPAREN, "Expect '(' after 'if'.")
        condition = self.expression()
        self.consume(TokenType.RPAREN, "Expect ')' after if condition.")
        then_branch = self.statement()
        else_branch = None
        if self.match(TokenType.ELSE):
            else_branch = self.statement()
        return If(condition, then_branch, else_branch)

    def print_statement(self):
        self.consume(TokenType.LPAREN, "Expect '(' after 'print'.")
        value = self.expression()
        self.consume(TokenType.RPAREN, "Expect ')' after print value.")
        self.consume(TokenType.SEMICOLON, "Expect ';' after value.")
        return Print(value)

    def return_statement(self):
        keyword = self.previous()
        value = None
        if not self.check(TokenType.SEMICOLON):
            value = self.expression()
        self.consume(TokenType.SEMICOLON, "Expect ';' after return value.")
        return Return(keyword, value)

    def while_statement(self):
        self.consume(TokenType.LPAREN, "Expect '(' after 'while'.")
        condition = self.expression()
        self.consume(TokenType.RPAREN, "Expect ')' after condition.")
        body = self.statement()
        return While(condition, body)

    def block(self):
        statements = []
        while not self.check(TokenType.RBRACE) and not self.is_at_end():
            statements.append(self.declaration())
        self.consume(TokenType.RBRACE, "Expect '}' after block.")
        return statements

    def expression_statement(self):
        expr = self.expression()
        self.consume(TokenType.SEMICOLON, "Expect ';' after expression.")
        return Expression(expr)



    def expression(self):
        return self.assignment()

    def assignment(self):
        expr = self.logic_or()
        if self.match(TokenType.EQ):
            equals = self.previous()
            value = self.assignment()
            if isinstance(expr, Variable):
                name = expr.name
                return Assign(name, value)
            elif isinstance(expr, GetIndex):
                return SetIndex(expr.callee, expr.index, value)
            raise Exception(f"Invalid assignment target at line {equals.line}")
        return expr

    def logic_or(self):
        expr = self.logic_and()
        while self.match(TokenType.OR):
            operator = self.previous()
            right = self.logic_and()
            expr = Binary(expr, operator, right)
        return expr

    def logic_and(self):
        expr = self.equality()
        while self.match(TokenType.AND):
            operator = self.previous()
            right = self.equality()
            expr = Binary(expr, operator, right)
        return expr

    def equality(self):
        expr = self.comparison()
        while self.match(TokenType.BANG_EQ, TokenType.EQ_EQ):
            operator = self.previous()
            right = self.comparison()
            expr = Binary(expr, operator, right)
        return expr

    def comparison(self):
        expr = self.term()
        while self.match(TokenType.GT, TokenType.GE, TokenType.LT, TokenType.LE):
            operator = self.previous()
            right = self.term()
            expr = Binary(expr, operator, right)
        return expr

    def term(self):
        expr = self.factor()
        while self.match(TokenType.MINUS, TokenType.PLUS):
            operator = self.previous()
            right = self.factor()
            expr = Binary(expr, operator, right)
        return expr

    def factor(self):
        expr = self.unary()
        while self.match(TokenType.SLASH, TokenType.STAR, TokenType.MODULO):
            operator = self.previous()
            right = self.unary()
            expr = Binary(expr, operator, right)
        return expr

    def unary(self):
        if self.match(TokenType.BANG, TokenType.MINUS):
            operator = self.previous()
            right = self.unary()
            return Unary(operator, right)
        return self.call()

    def call(self):
        expr = self.primary()
        while True:
            if self.match(TokenType.LPAREN):
                expr = self.finish_call(expr)
            elif self.match(TokenType.LBRACKET):
                index = self.expression()
                self.consume(TokenType.RBRACKET, "Expect ']' after index.")
                expr = GetIndex(expr, index)
            else:
                break
        return expr

    def finish_call(self, callee):
        arguments = []
        if not self.check(TokenType.RPAREN):
            while True:
                arguments.append(self.expression())
                if not self.match(TokenType.COMMA): break
        paren = self.consume(TokenType.RPAREN, "Expect ')' after arguments.")
        return Call(callee, paren, arguments)

    def primary(self):
        if self.match(TokenType.FALSE): return Literal(False)
        if self.match(TokenType.TRUE): return Literal(True)
        if self.match(TokenType.NIL): return Literal(None)
        if self.match(TokenType.NULL): return Literal(PyMiniNull())
        if self.match(TokenType.NUMBER, TokenType.STRING):
            return Literal(self.previous().literal)
        if self.match(TokenType.IDENTIFIER):
            return Variable(self.previous())
        if self.match(TokenType.LPAREN):
            expr = self.expression()
            self.consume(TokenType.RPAREN, "Expect ')' after expression.")
            return Grouping(expr)
        if self.match(TokenType.LBRACKET):
            elements = []
            if not self.check(TokenType.RBRACKET):
                while True:
                    elements.append(self.expression())
                    if not self.match(TokenType.COMMA): break
            self.consume(TokenType.RBRACKET, "Expect ']' after list elements.")
            return List(elements)
        if self.match(TokenType.LBRACE):
            entries = {}
            if not self.check(TokenType.RBRACE):
                while True:
                    key = self.consume(TokenType.STRING, "Expect string key in dict literal.")
                    self.consume(TokenType.COLON, "Expect ':' after key.")
                    value = self.expression()
                    entries[key.literal] = value
                    if not self.match(TokenType.COMMA): break
            self.consume(TokenType.RBRACE, "Expect '}' after dict literal.")
            return Dict(entries)
        raise Exception(f"Expect expression at line {self.peek().line}")

    def match(self, *types):
        for type in types:
            if self.check(type):
                self.advance()
                return True
        return False

    def check(self, type):
        if self.is_at_end(): return False
        return self.peek().type == type

    def advance(self):
        if not self.is_at_end(): self.current += 1
        return self.previous()

    def is_at_end(self):
        return self.peek().type == TokenType.EOF

    def peek(self):
        return self.tokens[self.current]

    def previous(self):
        return self.tokens[self.current - 1]

    def consume(self, type, message):
        if self.check(type): return self.advance()
        raise Exception(f"{message} at line {self.peek().line}")

    def synchronize(self):
        self.advance()
        while not self.is_at_end():
            if self.previous().type == TokenType.SEMICOLON: return
            if self.peek().type in [TokenType.FUNC, TokenType.LET, TokenType.IF, TokenType.WHILE, TokenType.PRINT, TokenType.RETURN]:
                return
            self.advance()

# --- Interpreter Classes ---
class ReturnException(Exception):
    def __init__(self, value):
        self.value = value

class Environment:
    def __init__(self, enclosing=None):
        self.values = {}
        self.enclosing = enclosing

    def define(self, name, value):
        self.values[name] = value

    def get(self, name):
        if name.lexeme in self.values:
            return self.values[name.lexeme]
        if self.enclosing:
            return self.enclosing.get(name)
        raise Exception(f"Undefined variable '{name.lexeme}' at line {name.line}")

    def assign(self, name, value):
        if name.lexeme in self.values:
            self.values[name.lexeme] = value
            return
        if self.enclosing:
            self.enclosing.assign(name, value)
            return
        raise Exception(f"Undefined variable '{name.lexeme}' at line {name.line}")

class PyMiniCallable:
    def call(self, interpreter, arguments):
        pass
    def arity(self):
        return 0

import time

class ClockFunction(PyMiniCallable):
    def arity(self):
        return 0

    def call(self, interpreter, arguments):
        return time.time()

class LenFunction(PyMiniCallable):
    def arity(self):
        return 1

    def call(self, interpreter, arguments):
        if not isinstance(arguments[0], (str, bytes, list)):
            raise Exception("len() expects a string, bytes, or list argument.")
        return len(arguments[0])

class BytesFromListFunction(PyMiniCallable):
    def arity(self):
        return 1

    def call(self, interpreter, arguments):
        if not isinstance(arguments[0], list):
            raise Exception("bytes_from_list() expects a list of integers.")
        return bytes(arguments[0])

class GetDictValueFunction(PyMiniCallable):
    def arity(self):
        return 2

    def call(self, interpreter, arguments):
        if not isinstance(arguments[0], dict):
            raise Exception("get_dict_value() expects a dictionary as the first argument.")
        return arguments[0].get(arguments[1])

class PyMiniNull:
    _instance = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(PyMiniNull, cls).__new__(cls)
        return cls._instance
    def __eq__(self, other):
        return isinstance(other, PyMiniNull)
    def __str__(self):
        return "null"

class IsNullFunction(PyMiniCallable):
    def arity(self):
        return 1
    def call(self, interpreter, arguments):
        return isinstance(arguments[0], PyMiniNull)

class DictSizeFunction(PyMiniCallable):
    def arity(self):
        return 1
    def call(self, interpreter, arguments):
        if not isinstance(arguments[0], dict):
            raise Exception("dict_size() expects a dictionary argument.")
        return len(arguments[0])

class ExplainFunction(PyMiniCallable):
    def arity(self):
        return 1
    def call(self, interpreter, arguments):
        message = interpreter.stringify(arguments[0])
        print(f"EXPLAIN: {message}")
        interpreter.trace.append(message)
        return PyMiniNull()

class GetExplanationsFunction(PyMiniCallable):
    def arity(self):
        return 0
    def call(self, interpreter, arguments):
        return list(interpreter.trace)

class RandomFunction(PyMiniCallable):
    def arity(self):
        return 0
    def call(self, interpreter, arguments):
        raise Exception("random() is blocked in strict mode.")

class NowFunction(PyMiniCallable):
    def arity(self):
        return 0
    def call(self, interpreter, arguments):
        raise Exception("now() is blocked in strict mode.")

class PyMiniFunction(PyMiniCallable):
    def __init__(self, declaration, closure):
        self.declaration = declaration
        self.closure = closure

    def arity(self):
        return len(self.declaration.params)

    def call(self, interpreter, arguments):
        environment = Environment(self.closure)
        for i in range(len(self.declaration.params)):
            environment.define(self.declaration.params[i].lexeme, arguments[i])
        try:
            interpreter.execute_block(self.declaration.body, environment)
        except ReturnException as e:
            return e.value
        return None

# --- Rust Core Integration ---
try:
    import pymini_core
    RUST_CORE_AVAILABLE = True
except ImportError:
    RUST_CORE_AVAILABLE = False

class RustFunction(PyMiniCallable):
    def __init__(self, func, arity_count):
        self.func = func
        self.arity_count = arity_count

    def arity(self):
        return self.arity_count

    def call(self, interpreter, arguments):
        try:
            return self.func(*arguments)
        except Exception as e:
            raise Exception(f"Rust Core Error: {e}")

class Interpreter:
    def __init__(self):
        self.trace = []
        self.globals = Environment()
        self.globals.define("clock", ClockFunction())
        self.globals.define("len", LenFunction())
        self.globals.define("bytes_from_list", BytesFromListFunction())
        self.globals.define("get_dict_value", GetDictValueFunction())
        self.globals.define("is_null", IsNullFunction())
        self.globals.define("dict_size", DictSizeFunction())
        self.globals.define("explain", ExplainFunction())
        self.globals.define("get_explanations", GetExplanationsFunction())
        self.globals.define("random", RandomFunction())
        self.globals.define("now", NowFunction())
        
        if RUST_CORE_AVAILABLE:
            self.globals.define("solana_get_balance", RustFunction(pymini_core.get_balance, 2))
            self.globals.define("solana_get_account_data", RustFunction(pymini_core.get_account_data, 2))
            self.globals.define("solana_deserialize_simple_account", RustFunction(pymini_core.deserialize_simple_account, 1))
            
        self.environment = self.globals

    def interpret(self, statements):
        try:
            for statement in statements:
                if statement:
                    self.execute(statement)
        except Exception as e:
            print(f"Runtime Error: {e}")

    def execute(self, stmt):
        if isinstance(stmt, Expression):
            self.evaluate(stmt.expression)
        elif isinstance(stmt, Print):
            value = self.evaluate(stmt.expression)
            print(self.stringify(value))
        elif isinstance(stmt, Var):
            value = None
            if stmt.initializer:
                value = self.evaluate(stmt.initializer)
            self.environment.define(stmt.name.lexeme, value)
        elif isinstance(stmt, Block):
            self.execute_block(stmt.statements, Environment(self.environment))
        elif isinstance(stmt, If):
            if self.is_truthy(self.evaluate(stmt.condition)):
                self.execute(stmt.then_branch)
            elif stmt.else_branch:
                self.execute(stmt.else_branch)
        elif isinstance(stmt, While):
            while self.is_truthy(self.evaluate(stmt.condition)):
                self.execute(stmt.body)
        elif isinstance(stmt, ForIn):
            iterable = self.evaluate(stmt.iterable)
            if not isinstance(iterable, list):
                raise Exception(f"Can only iterate over lists at line {stmt.item.line}")
            
            for value in iterable:
                environment = Environment(self.environment)
                environment.define(stmt.item.lexeme, value)
                self.execute_block(stmt.body.statements if isinstance(stmt.body, Block) else [stmt.body], environment)
        elif isinstance(stmt, Function):
            function = PyMiniFunction(stmt, self.environment)
            self.environment.define(stmt.name.lexeme, function)
        elif isinstance(stmt, Return):
            value = None
            if stmt.value:
                value = self.evaluate(stmt.value)
            raise ReturnException(value)
        elif isinstance(stmt, TryCatch):
            try:
                self.execute_block(stmt.try_block, Environment(self.environment))
            except Exception as e:
                # Scoped environment for catch block
                catch_env = Environment(self.environment)
                catch_env.define(stmt.catch_var.lexeme, str(e))
                self.execute_block(stmt.catch_block, catch_env)

    def execute_block(self, statements, environment):
        previous = self.environment
        try:
            self.environment = environment
            for statement in statements:
                if statement:
                    self.execute(statement)
        finally:
            self.environment = previous

    def evaluate(self, expr):
        if isinstance(expr, Literal):
            return expr.value
        elif isinstance(expr, List):
            return [self.evaluate(element) for element in expr.elements]
        elif isinstance(expr, Dict):
            return {key: self.evaluate(value) for key, value in expr.entries.items()}
        elif isinstance(expr, GetIndex):
            callee = self.evaluate(expr.callee)
            index = self.evaluate(expr.index)
            if not isinstance(callee, (list, str, bytes, dict)):
                raise Exception("Can only index into lists, strings, bytes, or dicts.")
            return callee[index]
        elif isinstance(expr, SetIndex):
            callee = self.evaluate(expr.callee)
            index = self.evaluate(expr.index)
            value = self.evaluate(expr.value)
            if not isinstance(callee, (list, dict)):
                raise Exception("Can only set index on lists or dicts.")
            callee[index] = value
            return value
        elif isinstance(expr, Grouping):
            return self.evaluate(expr.expression)
        elif isinstance(expr, Unary):
            right = self.evaluate(expr.right)
            if expr.operator.type == TokenType.MINUS:
                return -float(right)
            if expr.operator.type == TokenType.BANG:
                return not self.is_truthy(right)
            self.check_number_operand(expr.operator, right)
        elif isinstance(expr, Binary):
            left = self.evaluate(expr.left)
            right = self.evaluate(expr.right)
            op_type = expr.operator.type
            if op_type == TokenType.PLUS:
                if isinstance(left, (int, float)) and isinstance(right, (int, float)):
                    return left + right
                if isinstance(left, str) and isinstance(right, str):
                    return left + right
                raise Exception(f"Operands must be two numbers or two strings at line {expr.operator.line}")
            if op_type == TokenType.AND:
                return self.is_truthy(left) and self.is_truthy(right)
            if op_type == TokenType.OR:
                return self.is_truthy(left) or self.is_truthy(right)
            if op_type == TokenType.MINUS:
                self.check_number_operands(expr.operator, left, right)
                return left - right
            if op_type == TokenType.SLASH:
                self.check_number_operands(expr.operator, left, right)
                return left / right
            if op_type == TokenType.STAR:
                self.check_number_operands(expr.operator, left, right)
                return left * right
            if op_type == TokenType.MODULO:
                self.check_number_operands(expr.operator, left, right)
                return left % right
            if op_type == TokenType.GT: return left > right
            if op_type == TokenType.GE: return left >= right
            if op_type == TokenType.LT: return left < right
            if op_type == TokenType.LE: return left <= right
            if op_type == TokenType.BANG_EQ: return left != right
            if op_type == TokenType.EQ_EQ: return left == right
        elif isinstance(expr, Variable):
            return self.environment.get(expr.name)
        elif isinstance(expr, Assign):
            value = self.evaluate(expr.value)
            self.environment.assign(expr.name, value)
            return value
        elif isinstance(expr, Call):
            callee = self.evaluate(expr.callee)
            arguments = []
            for argument in expr.arguments:
                arguments.append(self.evaluate(argument))
            if not isinstance(callee, PyMiniCallable):
                raise Exception(f"Can only call functions and classes at line {expr.paren.line}")
            if len(arguments) != callee.arity():
                raise Exception(f"Expected {callee.arity()} arguments but got {len(arguments)} at line {expr.paren.line}")
            return callee.call(self, arguments)
        return None

    def is_truthy(self, obj):
        if obj is None: return False
        if isinstance(obj, bool): return obj
        return True

    def stringify(self, obj):
        if obj is None: return "nil"
        if isinstance(obj, PyMiniNull): return "null"
        if isinstance(obj, bool):
            return "true" if obj else "false"
        if isinstance(obj, dict):
            items = [f'"{k}": {self.stringify(v)}' for k, v in obj.items()]
            return "{" + ", ".join(items) + "}"
        return str(obj)

    def check_number_operand(self, operator, operand):
        if isinstance(operand, (int, float)): return
        raise Exception(f"Operand must be a number at line {operator.line}")

    def check_number_operands(self, operator, left, right):
        if isinstance(left, (int, float)) and isinstance(right, (int, float)): return
        raise Exception(f"Operands must be numbers at line {operator.line}")

# --- Main Entry Point ---
class PyMini:
    def __init__(self):
        self.interpreter = Interpreter()

    def run_file(self, path):
        with open(path, 'r') as f:
            self.run(f.read())

    def run_prompt(self):
        print("PyMini REPL (type 'exit' to quit)")
        while True:
            try:
                line = input("> ")
                if line == "exit": break
                self.run(line)
            except EOFError:
                break
            except Exception as e:
                print(e)

    def run(self, source):
        lexer = Lexer(source)
        tokens = lexer.scan_tokens()
        parser = Parser(tokens)
        statements = parser.parse()
        self.interpreter.interpret(statements)

if __name__ == "__main__":
    pymini = PyMini()
    if len(sys.argv) > 2:
        print("Usage: python3 pymini.py [script]")
        sys.exit(64)
    elif len(sys.argv) == 2:
        pymini.run_file(sys.argv[1])
    else:
        pymini.run_prompt()
