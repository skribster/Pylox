import sys

import expr as Expr
import stmt as Stmt
from interpreter import Interpreter

from tokens import Token
from errors import ResolverError

from enum import Enum

class FunctionType(Enum):
    NONE = 0,
    FUNCTION = 1,
    INITIALIZER = 2,
    METHOD = 3

class ClassType(Enum):
    NONE = 1,
    CLASS = 2,
    SUBCLASS = 3


class Resolver(Expr.ExprVisitor, Stmt.StmtVisitor):
    def __init__(self, interpreter : Interpreter):
        self.interpreter = interpreter
        self.scopes = []
        self.current_function = FunctionType.FUNCTION
        self.current_class = ClassType.NONE

    def resolve(self, construct : list[Stmt.Stmt] | Stmt.Stmt | Expr.Expr):
        try:
            if isinstance(construct, list):
                for statement in construct:
                    self.resolve(statement)

            elif isinstance(construct, Stmt.Stmt):
                construct.accept(self)

            elif isinstance(construct, Expr.Expr):
                construct.accept(self)

        except ResolverError as error:
            print(error, file=sys.stderr)

    def visit_block_stmt(self, stmt):
        self.begin_scope()
        self.resolve(stmt.statements)
        self.end_scope()
        return None
    
    def visit_class_stmt(self, stmt):
        enclosing_class = self.current_class
        self.current_class = ClassType.CLASS

        self.declare(stmt.name)
        self.define(stmt.name)

        if stmt.superclass is not None \
            and stmt.name.lexeme == stmt.superclass.name.lexeme:
            raise ResolverError(stmt.superclass.name, "A class cannot inherit from itself.")

        if stmt.superclass is not None:
            self.current_class = ClassType.SUBCLASS
            self.resolve(stmt.superclass)

        if stmt.superclass is not None:
            self.begin_scope()
            self.scopes[-1]["super"] = True

        self.begin_scope()

        # Define "this"
        top_scope = self.scopes[-1]
        top_scope["this"] = True

        for method in stmt.methods:
            declaration = FunctionType.METHOD
            if method.name.lexeme == "init":
                declaration = FunctionType.INITIALIZER

            self.resolve_function(method.function, declaration)

        self.end_scope()

        if stmt.superclass is not None:
            self.end_scope()

        self.current_class = enclosing_class
        return None
    
    def visit_var_stmt(self, stmt):
        self.declare(stmt.name)

        if stmt.initializer is not None:
            self.resolve(stmt.initializer)

        self.define(stmt.name)

        return None
    
    def visit_function_stmt(self, stmt):
        self.declare(stmt.name)
        self.define(stmt.name)
        self.resolve_function(stmt.function, FunctionType.FUNCTION)

        return None
    
    def visit_expression_stmt(self, stmt):
        self.resolve(stmt.expression)
        return None
    
    def visit_if_stmt(self, stmt):
        self.resolve(stmt.condition)
        self.resolve(stmt.then_branch)
        if stmt.else_branch is not None:
            self.resolve(stmt.else_branch)

        return None
    
    def visit_print_stmt(self, stmt):
        self.resolve(stmt.expression)
        return None
    
    def visit_return_stmt(self, stmt):
        if self.current_function == FunctionType.NONE:
            raise ResolverError(stmt.keyword, "Cannot return from top-level code.")

        if stmt.value is not None:
            if self.current_function == FunctionType.INITIALIZER:
                raise ResolverError(stmt.keyword, "Cannot return a value from an initializer.")
            
            self.resolve(stmt.value)

        return None
    
    def visit_while_stmt(self, stmt):
        self.resolve(stmt.condition)
        self.resolve(stmt.body)
        return None

    def visit_for_stmt(self, stmt):
        self.resolve(stmt.initializer)
        self.resolve(stmt.body)
        self.resolve(stmt.update)
        return None
    
    def visit_break_stmt(self, stmt):
        return None
    
    def visit_continue_stmt(self, stmt):
        return None
    
    def visit_get_expr(self, expr):
        self.resolve(expr.object)
        return None
    
    def visit_set_expr(self, expr):
        self.resolve(expr.value)
        self.resolve(expr.object)
        return None
    
    def visit_super_expr(self, expr):
        if self.current_class == ClassType.NONE:
            raise ResolverError(expr.keyword, "Cannot use 'super' outside of a class.")
        
        elif self.current_class != ClassType.SUBCLASS:
            raise ResolverError(expr.keyword, "Cannot use 'super' in a class with no superclass.")

        self.resolve_local(expr, expr.keyword)
        return None
    
    def visit_this_expr(self, expr):
        if self.current_class == ClassType.NONE:
            raise ResolverError(expr.keyword, "Cannot use 'this' outside of a class.")

        self.resolve_local(expr, expr.keyword)
        return None
    
    def visit_variable_expr(self, expr):
        scopes_empty = len(self.scopes) == 0

        # Checks if the variable is being accessed
        # inside its own initializer, like:
        # var a = a;
        if not scopes_empty and self.scopes[-1].get(expr.name.lexeme) == False:
            raise ResolverError(expr.name, "Cannot read local variable in its own initializer.")
    
        self.resolve_local(expr, expr.name)
        return None
    
    def visit_assign_expr(self, expr):
        self.resolve(expr.value)
        self.resolve_local(expr, expr.name)
        return None
    
    def visit_function_expr(self, expr):
        return None
    
    def visit_binary_expr(self, expr):
        self.resolve(expr.left)
        self.resolve(expr.right)
        return None
    
    def visit_call_expr(self, expr):
        self.resolve(expr.callee)

        for argument in expr.arguments:
            self.resolve(argument)

        return None
    
    def visit_grouping_expr(self, expr):
        self.resolve(expr.expression)
        return None
    
    def visit_literal_expr(self, expr):
        return None
    
    def visit_logical_expr(self, expr):
        self.resolve(expr.left)
        self.resolve(expr.right)
        return None
    
    def visit_unary_expr(self, expr):
        self.resolve(expr.right)
        return None

    # Helper functions
    

    def resolve_local(self, expr : Expr, name : Token):
        # Works through the stack top to bottom (reversed)
        # looking for a matching name. If we find
        # the variable we resolve it and pass
        # how many descents we had to take
        for depth, scope in enumerate(reversed(self.scopes)):
            if name.lexeme in scope:
                self.interpreter.resolve(expr, depth)
                return
            
    def resolve_function(self, function : Expr.Function, type : FunctionType):    
        last_function : FunctionType = self.current_function
        self.current_function = type

        self.begin_scope()
        for param in function.params:
            self.declare(param)
            self.define(param)

        self.resolve(function.body)
        self.end_scope()

        self.current_function = last_function

    def declare(self, name : Token):
        # NOTE: this does not declare anything
        # that isn't in an inner block. like a global
        if len(self.scopes) == 0:
            return
        
        # Get last element on top of stack
        scope = self.scopes[-1]
        if name.lexeme in scope:
            raise ResolverError(name, "Already a variable with this name in this scope.")

        scope[name.lexeme] = False

    def define(self, name : Token):
        if len(self.scopes) == 0:
            return
        
        # Get last element on top of stack
        scope = self.scopes[-1]
        scope[name.lexeme] = True 

    def begin_scope(self):
        self.scopes.append({})

    def end_scope(self):
        self.scopes.pop()
