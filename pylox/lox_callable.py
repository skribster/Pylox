from abc import ABC, abstractmethod
from typing import Any

class LoxCallable(ABC):
    @abstractmethod
    def call(interpreter, arguments : list[Any]):
        raise NotImplementedError
    
    def arity():
        raise NotImplementedError