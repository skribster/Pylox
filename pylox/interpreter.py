import sys
import time

import stmt as Stmt
import expr as Expr

from exceptions import ReturnException, BreakException, ContinueException
from environment import Environment
from typing import Any
from tokens import Token, TokenType as TT
from errors import InterpreterError

from lox_callable import LoxCallable
from lox_function import LoxFunction
from lox_class import LoxClass, LoxInstance


class Interpreter(Expr.ExprVisitor, Stmt.StmtVisitor):
    uninitialized = object()
    globals = Environment()
    environment = globals
    locals = {}

    def __init__(self):
        class Clock(LoxCallable):
            def arity(self) -> int:
                return 0
            
            def call(self, interpreter : Interpreter, arguments : list[Any]):
                return float(time.time_ns() / 1e9)
            
            def __str__(self):
                return "<native fn>"

        self.globals.define("clock", Clock())

    def interpret(self, input : list[Stmt.Stmt] | Expr.Expr):
        if isinstance(input, Expr.Expr):
            try: 
                value = self.evaluate(input)
                return value
            except InterpreterError as error:
                print(error, file=sys.stderr)
                return None
        
        try:
            for statement in input:
                self.execute(statement)

        except InterpreterError as error:
            print(error, file=sys.stderr)

    # Similar to execute() but for statements instead of expressions
    def execute(self, stmt : Stmt.Stmt):
        stmt.accept(self)

    def resolve(self, expr : Expr, depth : int):
        self.locals[expr] = depth

    def execute_block(self, statements : list[Stmt.Stmt], environment : Environment):
        previous = self.environment

        # self.environment now represents the current
        # environment/block/scope. 

        try:
            self.environment = environment
            for statement in statements:
                self.execute(statement)

        finally:
            # Exit out of the current scope
            # and refer to the previous one
            self.environment = previous

    def evaluate(self, expr : Expr.Expr):
        return expr.accept(self)
    
    def visit_return_stmt(self, stmt):
        value : Any = None
        if stmt.value is not None:
            value = self.evaluate(stmt.value)

        raise ReturnException(value)
    
    def visit_function_stmt(self, stmt : Stmt.Function):
        func_body = LoxFunction(stmt.function, self.environment, False)
        self.environment.define(stmt.name.lexeme, func_body)

        return None
    
    def visit_if_stmt(self, stmt):
        condition_result = self.evaluate(stmt.condition)
        if self.is_truthy(condition_result):
            self.execute(stmt.then_branch)
        elif stmt.else_branch is not None:
            self.execute(stmt.else_branch)

        return None
    
    def visit_block_stmt(self, stmt):
        scope = Environment(enclosing = self.environment)
        self.execute_block(stmt.statements, scope)
        return None
    
    def visit_class_stmt(self, stmt):
        superclass = None

        if stmt.superclass is not None:
            superclass = self.evaluate(stmt.superclass)
            if not isinstance(superclass, LoxClass):
                raise InterpreterError(stmt.superclass.name, "Superclass must be a class.")

        self.environment.define(stmt.name.lexeme, None)

        if stmt.superclass is not None:
            self.environment = Environment(self.environment)
            self.environment.define("super", superclass)

        methods = {}
        for method in stmt.methods:
            new_function = LoxFunction(method.function, self.environment, method.name.lexeme == "init")
            methods[method.name.lexeme] = new_function

        klass = LoxClass(stmt.name.lexeme, superclass, methods)
        if superclass is not None:
            self.environment = self.environment.enclosing
        
        self.environment.assign(stmt.name, klass)

        return None
    
    def visit_expression_stmt(self, stmt):
        self.evaluate(stmt.expression)
        return None
    
    def visit_print_stmt(self, stmt):
        value = self.evaluate(stmt.expression)
        print(self.stringify(value))
        return None

    def visit_var_stmt(self, stmt):
        value = Interpreter.uninitialized
        if stmt.initializer is not None:
            # figure out the expression for the variable
            # like if you were to assign var = 3 + 5;
            # we're gonna have to figure out what 3 + 5 is
            value = self.evaluate(stmt.initializer)

        self.environment.define(stmt.name.lexeme, value)
        
        return None
    
    def visit_break_stmt(self, stmt):
        raise BreakException()
    
    def visit_continue_stmt(self, stmt):
        raise ContinueException()
    
    def visit_while_stmt(self, stmt : Stmt.While):
        try:
            while self.is_truthy(self.evaluate(stmt.condition)):
                try: self.execute(stmt.body)
                except ContinueException: continue

        except BreakException:
            pass
    
        return None
    
    def visit_for_stmt(self, stmt):
        try:
            self.execute(stmt.initializer)
            while self.is_truthy(self.evaluate(stmt.condition)):
                try: self.execute(stmt.body)
                except ContinueException: continue
                finally: 
                    if stmt.update is not None: self.execute(stmt.update)

        except BreakException:
            pass

        return None
    
    def visit_function_expr(self, expr):
        return LoxFunction(expr, self.environment)
    
    def visit_assign_expr(self, expr):
        value = self.evaluate(expr.value)

        # The hash map returns a distance for each key
        distance : int = self.locals.get(expr)
        if distance is not None:
            self.environment.assign_at(distance, expr.name, value)
        else:
            self.globals.assign(expr.name, value)
        
        return value

    def visit_binary_expr(self, expr):
        left = self.evaluate(expr.left)
        right = self.evaluate(expr.right)

        match expr.operator.type:
            case TT.GREATER:
                self.check_number_operands(expr.operator, left, right)
                return float(left) > float(right)
            case TT.GREATER_EQUAL:
                self.check_number_operands(expr.operator, left, right)
                return float(left) >= float(right)
            case TT.LESS:
                self.check_number_operands(expr.operator, left, right)
                return float(left) < float(right)
            case TT.LESS_EQUAL:
                self.check_number_operands(expr.operator, left, right)
                return float(left) <= float(right)
            case TT.SLASH:
                self.check_number_operands(expr.operator, left, right)
                return float(left) / float(right)
            case TT.BANG_EQUAL:
                return not self.is_equal(left, right)
            case TT.EQUAL_EQUAL:
                return self.is_equal(left, right)
            case TT.STAR:
                self.check_number_operands(expr.operator, left, right)
                return float(left) * float(right)
            case TT.MINUS:
                self.check_number_operands(expr.operator, left, right)
                return float(left) - float(right)
            case TT.PLUS:
                if isinstance(left, float) and isinstance(right, float):
                    return float(left) + float(right)
                
                if isinstance(left, str) or isinstance(right, str):
                    return self.stringify(left) + self.stringify(right)

                if isinstance(left, str) and isinstance(right, str):
                    return str(left) + str(right)
                
                raise InterpreterError(expr.operator, "Operands must be two numbers or two strings.")
            
        return None
    
    def visit_call_expr(self, expr):
        callee = self.evaluate(expr.callee)
        arguments : list[Any] = []

        for argument in expr.arguments:
            arguments.append(self.evaluate(argument))

        # Assume callee is a LoxCallable
        if not isinstance(callee, LoxCallable):
            raise InterpreterError(expr.paren, "Can only call functions and classes.")

        if len(arguments) != callee.arity():
            raise InterpreterError(
                expr.paren, 
                "Expected " + str(callee.arity()) + " arguments but got " + str(len(arguments) + 1) + "."
            )

        return callee.call(self, arguments)
    
    def visit_get_expr(self, expr):
        object = self.evaluate(expr.object)
        if isinstance(object, LoxInstance):
            return object.get(expr.name)
        
        raise InterpreterError(expr.name, "Only instances have properties.")

    def visit_grouping_expr(self, expr):
        return self.evaluate(expr.expression)

    def visit_literal_expr(self, expr : Expr.Literal):
        return expr.value
    
    def visit_logical_expr(self, expr):
        left_result = self.evaluate(expr.left)

        if expr.operator.type == TT.OR:
            # > left_expr or right_expr
            # Check if the left expression is true
            # If so, we return the left expression's result
            # If not, we return the right expression's result
            if self.is_truthy(left_result): return left_result
        else:
            # > left_expr and right_expr
            # Check if the left expression is true
            # If so, we return the right expression's result
            # If not, we simply return left result
            if not self.is_truthy(left_result): return left_result

        return self.evaluate(expr.right)
    
    def visit_set_expr(self, expr):
        object = self.evaluate(expr.object)

        if not isinstance(object, LoxInstance):
            raise InterpreterError(expr.name, "Only instances have fields.")
        
        value = self.evaluate(expr.value)
        object.set(expr.name, value)

        return value
    
    def visit_super_expr(self, expr):
        distance = self.locals.get(expr)
        superclass = self.environment.get_at(
            distance, "super"
        )

        object = self.environment.get_at(
            distance - 1, "this"
        )

        method : LoxFunction= superclass.find_method(expr.method.lexeme)
        if method is None:
            raise InterpreterError(
                expr.method, 
                "Undefined property '" + expr.method.lexeme + "'."
            )
        
        return method.bind(object)
    
    def visit_this_expr(self, expr):
        return self.look_up_variable(expr.keyword, expr)
    
    def visit_unary_expr(self, expr):
        right = self.evaluate(expr.right)
        
        match expr.operator.type:
            case TT.BANG:
                return not self.is_truthy(right)
            case TT.MINUS:
                self.check_number_operand(expr.operator, right)
                return -float(right)
            
        return None
    
    def visit_variable_expr(self, expr):
        return self.look_up_variable(expr.name, expr)
    
    ### HEPLPER FUNCTIONS ###
    def look_up_variable(self, name : Token, expr : Expr):
        distance : int = self.locals.get(expr)
        if distance is not None:
            return self.environment.get_at(distance, name.lexeme)
        else:
            return self.globals.get(name)

    def is_truthy(self, object : Any):
        if object is None:
            return False
        
        if isinstance(object, bool):
            return bool(object)
        
        # Anything that exists is considered true
        return True
    
    def is_equal(self, a : Any, b : Any):
        if (a is None and b is None):
            return True
        if (a is None):
            return False
        
        return a == b
    
    def check_number_operand(self, operator : Token, operand : Any):
        if isinstance(operand, float): return
        raise InterpreterError(operator, "Operand must be a number.")

    def check_number_operands(self, operator : Token, left : Any, right : Any):
        if isinstance(left, float) and isinstance(right, float):
            return
        
        raise InterpreterError(operator, "Operands must be numbers.")
    
    @staticmethod
    def stringify(object : Any):
        if object is None:
            return "nil"
        
        if isinstance(object, float):
            text = str(object)

            if text.endswith(".0"):
                text = text[0 : len(text) - 2]

            return text
        
        return str(object)
    