import sys

from errors import ParseError
from tokens import Token, TokenType as TT
import expr as Expr
import stmt as Stmt

"""
RULES:
expression     → equality ;
equality       → comparison ( ( "!=" | "==" ) comparison )* ;
comparison     → term ( ( ">" | ">=" | "<" | "<=" ) term )* ;
term           → factor ( ( "-" | "+" ) factor )* ;
factor         → unary ( ( "/" | "*" ) unary )* ;
unary          → ( "!" | "-" ) unary
               | primary ;
primary        → NUMBER | STRING | "true" | "false" | "nil"
               | "(" expression ")" ;

THINGS TO NOTE FOR ME:               
* The parser automatically advances everytime it
  evaluates a token/expression
* Every expression winds back to the variable
  that called it :)

"""


class Parser:  
    def __init__(self, tokens : list[Token]):
        self.tokens = tokens
        self.current = 0

        self.loop_depth = 0
        self.allow_expression = False
        self.found_expression = False

    def parse(self):
        statements = []
        while not self.is_at_end():
            statements.append(self.declaration())

        return statements
    
    def parse_repl(self):
        self.allow_expression = True
        
        statements = []
        while not self.is_at_end():
            statements.append(self.declaration())

            if self.found_expression:
                last = statements[len(statements) - 1]
                return last.expression

            self.allow_expression = False

        return statements

    def declaration(self):
        try:
            if self.match(TT.VAR):
                return self.var_declaration()
            if self.check(TT.FUN) and self.check_next(TT.IDENTIFIER):
                self.consume(TT.FUN, None)
                return self.function("function")
            if self.match(TT.CLASS):
                return self.class_declaration()
            
            return self.statement()
        
        except ParseError as error:
            print(error, file=sys.stderr)
            self.synchronize()
            return None
        
    def class_declaration(self):
        name = self.consume(TT.IDENTIFIER, "Expected class name.")
        
        superclass : Expr.Variable = None
        if self.match(TT.LESS):
            self.consume(TT.IDENTIFIER, "Expected superclass name.")
            superclass = Expr.Variable(self.previous())
        
        self.consume(TT.LEFT_BRACE, "Expected '{' before class body.")

        methods : list[Stmt.Function] = []
        while not self.check(TT.RIGHT_BRACE) and not self.is_at_end():
            methods.append(self.function("method"))

        self.consume(TT.RIGHT_BRACE, "Expected '}' after class body.")

        return Stmt.Class(name, superclass, methods)
        
    # For specifically named functions
    def function(self, kind : str) -> Stmt.Function:
        name : Token = self.consume(TT.IDENTIFIER, "Expected " + kind + " name.")
        return Stmt.Function(name, self.function_body(kind, name))
    
    # For anonymous functions
    def function_body(self, kind : str, name : Token | None = None) -> Expr.Function:
        self.consume(TT.LEFT_PAREN, "Expected '(' after " + kind + " name.")
        parameters : list[Token] = []
        
        if not self.check(TT.RIGHT_PAREN):
            while True:
                if len(parameters) >= 255:
                    raise ParseError(self.peek(), "Cannot have more than 255 parameters.")
            
                argument_name = self.consume(TT.IDENTIFIER, "Expected parameter name.")
                parameters.append(argument_name)

                if not (self.match(TT.COMMA)): break


        self.consume(TT.RIGHT_PAREN, "Expected ')' after parameters.")

        # block() already assumes that the opening brace token
        # has already been matched :)
        self.consume(TT.LEFT_BRACE, "Expected '{' before " + kind + " body.")
        body : list[Stmt.Stmt] = self.block()

        return Expr.Function(parameters, body)
        
    def var_declaration(self):
        name = self.consume(TT.IDENTIFIER, "Expected variable name.")

        initializer = None
        if self.match(TT.EQUAL):
            initializer = self.expression()

        self.consume(TT.SEMICOLON, "Expected ';' after variable declaration.")
        return Stmt.Var(name, initializer)
        
    def statement(self):
        if self.match(TT.PRINT):
            return self.print_statement()
        if self.match(TT.LEFT_BRACE):
            return Stmt.Block(self.block())
        if self.match(TT.IF):
            return self.if_statement()
        if self.match(TT.WHILE):
            return self.while_statement()
        if self.match(TT.FOR):
            return self.for_statement()
        if self.match(TT.BREAK):
            return self.break_statement()
        if self.match(TT.CONTINUE):
            return self.continue_statement()
        if self.match(TT.RETURN):
            return self.return_statement()
        
        return self.expression_statement()
    
    def return_statement(self):
        keyword = self.previous()
        value : Expr = None

        if not self.check(TT.SEMICOLON):
            value = self.expression()

        self.consume(TT.SEMICOLON, "Expected ';' after return value.")
        return Stmt.Return(keyword, value)
    
    def break_statement(self):
        if self.loop_depth == 0:
            raise ParseError(self.peek(), "No loop to break outside of")

        self.consume(TT.SEMICOLON, "Expected ';' after 'break'.")
        return Stmt.Break()
    
    def continue_statement(self):
        if self.loop_depth == 0:
            raise ParseError(self.peek(), "No loop to continue inside of")

        self.consume(TT.SEMICOLON, "Expected ';' after 'continue'.")
        return Stmt.Continue()
    
    def for_statement(self):
        try:
            self.loop_depth += 1
            self.consume(TT.LEFT_PAREN, "Expected '(' after 'for'.")
        
            # Each part of the for loop can be left out optionally.
            initializer : Stmt
            if self.match(TT.SEMICOLON):
                initializer = None
            elif self.match(TT.VAR):
                initializer = self.var_declaration()
            else:
                initializer = self.expression_statement()

            condition : Stmt = None
            if not self.check(TT.SEMICOLON):
                condition = self.expression()

            self.consume(TT.SEMICOLON, "Expected ';' after loop condition.")

            increment : Expr = None
            if not self.check(TT.RIGHT_PAREN):
                increment = self.expression()

            self.consume(TT.RIGHT_PAREN, "Expected ')' after for clauses.")

            # Body time
            body = self.statement()
            if condition is None:
                condition = Expr.Literal(True)

            body = Stmt.For(initializer, condition, increment, body)

            return body
        
        finally:
            self.loop_depth -= 1


    def while_statement(self):
        try:
            self.loop_depth += 1
            self.consume(TT.LEFT_PAREN, "Expected '(' after 'while'.")
            condition = self.expression()
            self.consume(TT.RIGHT_PAREN, "Expected ')' after condition.")

            body = self.statement()

            return Stmt.While(condition, body)
        finally:
            self.loop_depth -= 1

    def if_statement(self):
        self.consume(TT.LEFT_PAREN, "Expected ')' after 'if'.")
        condition = self.expression()
        self.consume(TT.RIGHT_PAREN, "Expected ')' after if condition.")

        then_branch = self.statement()
        else_branch = self.statement() if self.match(TT.ELSE) else None

        return Stmt.If(condition, then_branch, else_branch)

    def print_statement(self):
        # Since we already consumed the print token in
        # self.statement we don't need to do it here
        value = self.expression()
        self.consume(TT.SEMICOLON, "Expected ';' after value.")

        return Stmt.Print(value)
    
    def expression_statement(self) -> Stmt.Stmt:
        expr = self.expression()

        if self.allow_expression and self.is_at_end():
            self.found_expression = True
        else:

            self.consume(TT.SEMICOLON, "Expected ';' after expression.")

        return Stmt.Expression(expr)
    
    def block(self) -> list[Stmt.Stmt]:
        statements = []

        while not self.check(TT.RIGHT_BRACE) and not self.is_at_end():
            statements.append(self.declaration())

        self.consume(TT.RIGHT_BRACE, "Expected '}' after block.")

        return statements

    def expression(self) -> Expr.Expr:
        return self.assignment()
    
    def assignment(self) -> Expr.Expr:
        # Think of expressions like a = b = c,
        # we're going to have multiple nested
        # assignments

        expr = self.or_expression()

        if self.match(TT.EQUAL):
            equals = self.previous()

            # Recursively get the value 
            # of the right side.
            value = self.assignment()

            # Checking the left side of the assignment
            # to see if it's a variable. If so, it would
            # probably print something in the ASTPrinter
            # like Assign(name, value) e.x. Assign(a 3)
            if isinstance(expr, Expr.Variable):
                name = expr.name
                return Expr.Assign(name, value)
            elif isinstance(expr, Expr.Get):
                return Expr.Set(expr.object, expr.name, value)
            
            raise ParseError(equals, "Invalid assignment target.")

        return expr
    
    def or_expression(self) -> Expr.Expr:
        expr = self.and_expression()

        # It's a while loop since we want to capture
        # repeated or statements like
        # true or true or true or true or true ...
        while self.match(TT.OR):
            operator = self.previous()
            right = self.and_expression()
            expr = Expr.Logical(expr, operator, right)

        return expr

    def and_expression(self) -> Expr.Expr:
        expr = self.equality()

        while self.match(TT.AND):
            operator = self.previous()
            right = self.equality()
            expr = Expr.Logical(expr, operator, right)

        return expr

    def equality(self) -> Expr.Expr:
        expr = self.comparison()

        while self.match(TT.BANG_EQUAL, TT.EQUAL_EQUAL):
            operator = self.previous()
            right = self.comparison()
            expr = Expr.Binary(expr, operator, right)

        return expr
    
    def comparison(self) -> Expr.Expr:
        expr = self.term()

        while self.match(TT.GREATER, TT.GREATER_EQUAL, TT.LESS, TT.LESS_EQUAL):
            operator = self.previous()
            right = self.term()

            expr = Expr.Binary(expr, operator, right)

        return expr

    def term(self) -> Expr.Expr:
        expr = self.factor()

        while self.match(TT.MINUS, TT.PLUS):
            operator = self.previous()
            right = self.factor()

            expr = Expr.Binary(expr, operator, right)

        return expr
    
    def factor(self) -> Expr.Expr:
        expr = self.unary()

        while self.match(TT.SLASH, TT.STAR):
            operator = self.previous()
            right = self.unary()

            expr = Expr.Binary(expr, operator, right)

        return expr

    def unary(self) -> Expr.Expr:
        if self.match(TT.BANG, TT.MINUS):
            operator = self.previous()
            right = self.unary()

            return Expr.Unary(operator, right)
        
        return self.call()
    
    def call(self) -> Expr.Expr:
        expr = self.primary()

        while True:
            if self.match(TT.LEFT_PAREN):
                expr = self.finish_call(expr)
            elif self.match(TT.DOT):
                name = self.consume(TT.IDENTIFIER, "Expected property name after '.'.")
                expr = Expr.Get(expr, name)
            else:
                break

        return expr
    
    def primary(self):
        if self.match(TT.TRUE): return Expr.Literal(True)
        if self.match(TT.FALSE): return Expr.Literal(False)
        if self.match(TT.NIL): return Expr.Literal(None)

        if self.match(TT.NUMBER, TT.STRING):
            return Expr.Literal(self.previous().literal)
        
        if self.match(TT.SUPER):
            keyword = self.previous()
            self.consume(TT.DOT, "Expected '.' after 'super'.")
            method = self.consume(TT.IDENTIFIER, "Expected superclass method name.")

            return Expr.Super(keyword, method)

        if self.match(TT.IDENTIFIER):
            return Expr.Variable(self.previous())

        if self.match(TT.LEFT_PAREN):
            expr = self.expression()
            self.consume(TT.RIGHT_PAREN, "Expected ')' after expression.")

            return Expr.Grouping(expr)
        
        if self.match(TT.FUN):
            return self.function_body("function")
        
        if self.match(TT.THIS):
            return Expr.This(self.previous())
        
        raise ParseError(self.peek(), "Expected expression.")
    
    ### HELPER FUNCTIONS ###
    def finish_call(self, callee : Expr) -> Expr.Expr:
        # Helps to parse the argument list by
        # advancing through and adding any of the
        arguments : list[Expr.Expr] = []

        if not self.check(TT.RIGHT_PAREN):
            while True:
                if len(arguments) >= 255:
                    raise ParseError(self.peek(), "Cannot have more than 255 arguments")
                arguments.append(self.expression())

                if not self.match(TT.COMMA): break
        
        paren : Token = self.consume(TT.RIGHT_PAREN, "Expected ')' after arguments.")

        return Expr.Call(callee, paren, arguments)

    def synchronize(self):
        self.advance()

        while not self.is_at_end():
            if self.previous().type == TT.SEMICOLON:
                return
            
            match self.peek().type:
                case TT.CLASS | TT.FUN | TT.FUN | TT.VAR | TT.FOR \
                    | TT.IF | TT.WHILE | TT.PRINT | TT.RETURN:
                    return
                
            self.advance()

    def consume(self, type : TT, message : str):
        if self.check(type):
            return self.advance()
        
        raise ParseError(self.peek(), message)

    def match(self, *types : tuple[TT]) -> bool:
        for type in types:
            if self.check(type):
                self.advance()
                return True
            
        return False
    
    def check(self, type : TT) -> bool:
        if self.is_at_end():
            return False
        
        return self.peek().type == type

    def check_next(self, type : TT) -> bool:
        if self.is_at_end():
            return False
        
        if self.tokens[self.current + 1].type == TT.EOF:
            return False
        
        return self.tokens[self.current + 1].type == type
        
    def advance(self) -> Token:
        if not self.is_at_end():
            self.current += 1

        return self.previous()
    
    def is_at_end(self) -> bool:
        return self.peek().type == TT.EOF

    def peek(self) -> Token:        
        return self.tokens[self.current]
    
    def previous(self) -> Token:
        return self.tokens[self.current - 1]