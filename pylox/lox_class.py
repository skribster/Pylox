from typing import Any

from lox_callable import LoxCallable
from lox_function import LoxFunction
from tokens import Token
from errors import InterpreterError

class LoxInstance:
    def __init__(self, klass : LoxClass):
        self.klass = klass
        self.fields = {}

    def get(self, name : Token):
        if name.lexeme in self.fields:
            return self.fields.get(name.lexeme)
        
        method = self.klass.find_method(name.lexeme)
        if method is not None:
            return method.bind(self)

        raise InterpreterError(name, "Undefined property '" + name.lexeme + "'.")

    def set(self, name : Token, value : Any):
        self.fields[name.lexeme] = value

    def __str__(self):
        return self.klass.name + " instance"


class LoxClass(LoxCallable):
    def __init__(self, name : str, superclass : LoxClass, methods : dict[str : LoxFunction]):
        self.superclass = superclass
        self.name = name
        self.methods = methods

    def find_method(self, name : str):
        if name in self.methods:
            return self.methods[name]
        
        if self.superclass is not None:
            return self.superclass.find_method(name)
        
        return None
        
    def call(self, interpreter, arguments : list[Any]):
        instance = LoxInstance(self)

        initializer : LoxFunction = self.find_method("init")
        if initializer is not None:
            initializer.bind(instance).call(interpreter, arguments)

        return instance
    
    def arity(self):
        initializer : LoxFunction = self.find_method("init")
        if initializer is None: return 0

        return initializer.arity()
    
    def __str__(self):
        return self.name