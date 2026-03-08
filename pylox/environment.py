from typing import Any
from tokens import Token
from errors import InterpreterError


class Environment:
    def __init__(self, enclosing : Environment = None):
        self.values = {}
        self.enclosing = enclosing

    def define(self, name : str, value : Any):
        self.values[name] = value

    def get(self, name : Token) -> Any:
        if name.lexeme in self.values:
            value = self.values.get(name.lexeme)
            return value
        
        if self.enclosing is not None:
            return self.enclosing.get(name)
        
        raise InterpreterError(name, "Undefined variable '" + name.lexeme + "'.")
    
    def get_at(self, distance : int, name : str):
        return self.get_ancestor(distance).values.get(name)
    
    def get_ancestor(self, distance : int):
        # Ascends through the family tree
        # (distance) many times
        environment = self
        for i in range(distance):
            environment = environment.enclosing

        return environment

    def assign(self, name : Token, value : Any):
        if name.lexeme in self.values:
            self.values[name.lexeme] = value
            return
        
        # Check if the outer blocks have the variable
        if self.enclosing is not None:
            self.enclosing.assign(name, value)
            return
        
        raise InterpreterError(name, "Undefined variable '" + name.lexeme + "'.")
    
    def assign_at(self, distance : int, name : Token, value : Any):
        self.get_ancestor(distance).values[name.lexeme] = value