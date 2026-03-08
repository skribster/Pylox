import expr as Expr

from exceptions import ReturnException
from lox_callable import LoxCallable
from environment import Environment
from typing import Any

class LoxFunction(LoxCallable):
    def __init__(self, declaration : Expr.Function, closure : Environment, is_initializer : bool):
        self.declaration = declaration
        self.closure = closure
        self.is_initializer = is_initializer

    def bind(self, instance):
        environment = Environment(self.closure)
        environment.define("this", instance)

        # The function is bound to the instance, 
        # so the closure is the environment of the instance
        return LoxFunction(self.declaration, environment, self.is_initializer)

    def arity(self):
        return len(self.declaration.params)

    def call(self, interpreter, arguments : list[Any]):
        environment = Environment(self.closure)

        for i in range(len(self.declaration.params)):
            param_name = self.declaration.params[i]
            param_value = arguments[i]
            environment.define(param_name.lexeme, param_value)

        try:
            interpreter.execute_block(self.declaration.body, environment)
        except ReturnException as exception:
            if self.is_initializer: return self.closure.get_at(0, "this")
            return exception.args[0]
        
        if self.is_initializer: return self.closure.get_at(0, "this")
        return None