ast_output = []
ast_path = "pylox\generated_expr.py"

RULES = [
    "Assign     = name : Token, value : Expr",
    "Binary     = left : Expr, operator : Token, right : Expr",
    "Call       = callee : Expr, paren : Token, arguments : list[Expr]",
    "Get        = object : Expr, name : Token",
    "Set        = object : Expr, name : Token, value : Expr",
    "Super      = keyword : Token, method : Token",
    "This       = keyword : Token",
    "Grouping   = expression : Expr",
    "Literal    = value : Any",
    "Function   = params : list[Token], body : Stmt",
    "Unary      = operator : Token, right : Expr",
    "Logical    = left : Expr, operator : Token, right : Expr",
    "Variable   = name : Token" # The name is a token with type TT.IDENTIFIER
]


def define_rule(className : str, fieldList : str):
    # Constructor.
    ast_output.append("class " + className + "(Expr):")
    ast_output.append("    def __init__(self, " + fieldList + "):")
    
    # Store parameters in the fields
    fields = fieldList.split(", ")
    for field in fields:
        name = field.split(" : ")[0]
        ast_output.append("        self." + name + " = " + name)

    ast_output.append("    ")
    ast_output.append("    def accept(self, visitor : ExprVisitor):")
    ast_output.append("        return visitor.visit_" + className.lower() + "_expr(self)")
    ast_output.append("    ")
    ast_output.append("    ")

##### HEADER #####
ast_output.append("from abc import ABC, abstractmethod")
ast_output.append("from tokens import Token")
ast_output.append("from typing import Any")
ast_output.append("from stmt import Stmt")
ast_output.append("")
ast_output.append("")

ast_output.append("### EXPR ABSTRACT CLASS ###")
ast_output.append("class Expr(ABC):")
ast_output.append("    def __init__(self):")
ast_output.append("         raise NotImplementedError")
ast_output.append("")
ast_output.append("    @abstractmethod")
ast_output.append("    def accept(self, visitor : ExprVisitor):")
ast_output.append("        raise NotImplementedError")
ast_output.append("")
ast_output.append("")

##### GENERATING EXPRESSION VISITOR #####
ast_output.append("### EXPR VISITOR ABSTRACT CLASS ###")
ast_output.append("class ExprVisitor(ABC):")
for rule in RULES:
    className = rule.split("=")[0].strip()
    ast_output.append("    @abstractmethod")
    ast_output.append("    def visit_" + className.lower() + "_expr(self, expr : " + className + "):")
    ast_output.append("        raise NotImplementedError")
    ast_output.append("")

for rule in RULES:
    className = rule.split("=")[0].strip()
    fieldList = rule.split("=")[1].strip()

ast_output.append("")

##### GENERATING EXPRESSION CLASSES #####
ast_output.append("### EXPRESSIONS ###")
for rule in RULES:
    className = rule.split("=")[0].strip()
    fieldList = rule.split("=")[1].strip()

    define_rule(className, fieldList)



with open(ast_path, 'x') as file:
    file.write('\n'.join(ast_output))