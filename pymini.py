import re
import sys

# --- Token Types ---
class TokenType:
    # Keywords
    LET = 'LET'
    FUNC = 'FUNC'
    IF = 'IF'
    ELSE = 'ELSE'
    WHILE = 'WHILE'
    RETURN = 'RETURN'
    PRINT = 'PRINT'
    TRUE = 'TRUE'
    FALSE = 'FALSE'
    NIL = 'NIL'

    # Operators
    PLUS = 'PLUS'
    MINUS = 'MINUS'
    STAR = 'STAR'
    SLASH = 'SLASH'
    EQ = 'EQ'
    EQ_EQ = 'EQ_EQ'
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
    SEMICOLON = 'SEMICOLON'
    COMMA = 'COMMA'

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
        'return': TokenType.RETURN,
        'print': TokenType.PRINT,
        'true': TokenType.TRUE,
        'false': TokenType.FALSE,
        'nil': TokenType.NIL,
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
        elif char == ';':
            self.add_token(TokenType.SEMICOLON)
        elif char == ',':
            self.add_token(TokenType.COMMA)
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

class Function(Stmt):
    def __init__(self, name, params, body):
        self.name = name
        self.params = params
        self.body = body

class Return(Stmt):
    def __init__(self, keyword, value):
        self.keyword = keyword
        self.value = value

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
        if self.match(TokenType.LBRACE): return Block(self.block())
        return self.expression_statement()

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
        expr = self.equality()
        if self.match(TokenType.EQ):
            equals = self.previous()
            value = self.assignment()
            if isinstance(expr, Variable):
                name = expr.name
                return Assign(name, value)
            raise Exception(f"Invalid assignment target at line {equals.line}")
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
        while self.match(TokenType.SLASH, TokenType.STAR):
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
        if self.match(TokenType.NUMBER, TokenType.STRING):
            return Literal(self.previous().literal)
        if self.match(TokenType.IDENTIFIER):
            return Variable(self.previous())
        if self.match(TokenType.LPAREN):
            expr = self.expression()
            self.consume(TokenType.RPAREN, "Expect ')' after expression.")
            return Grouping(expr)
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

class Interpreter:
    def __init__(self):
        self.globals = Environment()
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
        elif isinstance(stmt, Function):
            function = PyMiniFunction(stmt, self.environment)
            self.environment.define(stmt.name.lexeme, function)
        elif isinstance(stmt, Return):
            value = None
            if stmt.value:
                value = self.evaluate(stmt.value)
            raise ReturnException(value)

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
        elif isinstance(expr, Grouping):
            return self.evaluate(expr.expression)
        elif isinstance(expr, Unary):
            right = self.evaluate(expr.right)
            if expr.operator.type == TokenType.MINUS:
                return -float(right)
            if expr.operator.type == TokenType.BANG:
                return not self.is_truthy(right)
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
            if op_type == TokenType.MINUS: return left - right
            if op_type == TokenType.SLASH: return left / right
            if op_type == TokenType.STAR: return left * right
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
        if isinstance(obj, bool):
            return "true" if obj else "false"
        return str(obj)

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
