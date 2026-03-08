from abc import ABC, abstractmethod
import expr as Expr
from tokens import Token


### STMT ABSTRACT CLASS ###
class Stmt(ABC):
    def __init__(self):
         raise NotImplementedError

    @abstractmethod
    def accept(self, visitor : StmtVisitor):
        raise NotImplementedError


### STMT VISITOR ABSTRACT CLASS ###
class StmtVisitor(ABC):
    @abstractmethod
    def visit_expression_stmt(self, stmt : Expression):
        raise NotImplementedError

    @abstractmethod
    def visit_function_stmt(self, stmt : Function):
        raise NotImplementedError

    @abstractmethod
    def visit_print_stmt(self, stmt : Print):
        raise NotImplementedError

    @abstractmethod
    def visit_var_stmt(self, stmt : Var):
        raise NotImplementedError

    @abstractmethod
    def visit_while_stmt(self, stmt : While):
        raise NotImplementedError

    @abstractmethod
    def visit_for_stmt(self, stmt : For):
        raise NotImplementedError

    @abstractmethod
    def visit_block_stmt(self, stmt : Block):
        raise NotImplementedError

    @abstractmethod
    def visit_class_stmt(self, stmt : Class):
        raise NotImplementedError

    @abstractmethod
    def visit_break_stmt(self, stmt : Break):
        raise NotImplementedError

    @abstractmethod
    def visit_continue_stmt(self, stmt : Continue):
        raise NotImplementedError

    @abstractmethod
    def visit_return_stmt(self, stmt : Return):
        raise NotImplementedError

    @abstractmethod
    def visit_if_stmt(self, stmt : If):
        raise NotImplementedError


### STATEMENTS ###
class Expression(Stmt):
    def __init__(self, expression : Expr.Expr):
        self.expression = expression
    
    def accept(self, visitor : StmtVisitor):
        return visitor.visit_expression_stmt(self)
    
    
class Function(Stmt):
    def __init__(self, name : Token, function : Expr.Function):
        self.name = name
        self.function = function
    
    def accept(self, visitor : StmtVisitor):
        return visitor.visit_function_stmt(self)
    
    
class Print(Stmt):
    def __init__(self, expression : Expr.Expr):
        self.expression = expression
    
    def accept(self, visitor : StmtVisitor):
        return visitor.visit_print_stmt(self)
    
    
class Var(Stmt):
    def __init__(self, name : Token, initializer : Expr):
        self.name = name
        self.initializer = initializer
    
    def accept(self, visitor : StmtVisitor):
        return visitor.visit_var_stmt(self)
    
    
class While(Stmt):
    def __init__(self, condition : Expr.Expr, body : Stmt):
        self.condition = condition
        self.body = body
    
    def accept(self, visitor : StmtVisitor):
        return visitor.visit_while_stmt(self)
    
    
class For(Stmt):
    def __init__(self, initializer : Expr.Expr | Stmt, condition : Expr.Expr, update : Stmt, body : Stmt):
        self.initializer = initializer
        self.condition = condition
        self.update = update
        self.body = body
    
    def accept(self, visitor : StmtVisitor):
        return visitor.visit_for_stmt(self)
    
    
class Block(Stmt):
    def __init__(self, statements : list[Stmt]):
        self.statements = statements
    
    def accept(self, visitor : StmtVisitor):
        return visitor.visit_block_stmt(self)
    
    
class Class(Stmt):
    def __init__(self, name : Token, superclass : Expr.Variable, methods : list[Function]):
        self.name = name
        self.superclass = superclass
        self.methods = methods
    
    def accept(self, visitor : StmtVisitor):
        return visitor.visit_class_stmt(self)
    
    
class Break(Stmt):
    def __init__(self):
        pass
    
    def accept(self, visitor : StmtVisitor):
        return visitor.visit_break_stmt(self)
    
    
class Continue(Stmt):
    def __init__(self):
        pass
    
    def accept(self, visitor : StmtVisitor):
        return visitor.visit_continue_stmt(self)
    
    
class Return(Stmt):
    def __init__(self, keyword : Token, value : Expr.Expr):
        self.keyword = keyword
        self.value = value
    
    def accept(self, visitor : StmtVisitor):
        return visitor.visit_return_stmt(self)
    
    
class If(Stmt):
    def __init__(self, condition : Expr.Expr, then_branch : Stmt, else_branch : Stmt):
        self.condition = condition
        self.then_branch = then_branch
        self.else_branch = else_branch
    
    def accept(self, visitor : StmtVisitor):
        return visitor.visit_if_stmt(self)
    
    