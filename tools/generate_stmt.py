ast_output = []
ast_path = "pylox/generated_stmt.py"

RULES = [
    "Expression     = expression : Expr.Expr",
    "Function       = name : Token, function : Expr.Function",
    "Print          = expression : Expr.Expr",
    "Var            = name : Token, initializer : Expr",
    "While          = condition : Expr.Expr, body : Stmt",
    "For            = initializer : Expr.Expr | Stmt, condition : Expr.Expr, update : Stmt, body : Stmt",
    "Block          = statements : list[Stmt]",
    "Class          = name : Token, superclass : Expr.Variable, methods : list[Function]",
    "Break          = ",
    "Continue       = ",
    "Return         = keyword : Token, value : Expr.Expr",
    "If             = condition : Expr.Expr, then_branch : Stmt, else_branch : Stmt"
]


def define_rule(className : str, fieldList : str):
    # Constructor.
    ast_output.append("class " + className + "(Stmt):")

    if fieldList != "":
        ast_output.append("    def __init__(self, " + fieldList + "):")
    else:
        ast_output.append("    def __init__(self):")
        ast_output.append("        pass")
    
    # Store parameters in the fields
    if fieldList != "":
        fields = fieldList.split(", ")
        for field in fields:
            name = field.split(" : ")[0]
            ast_output.append("        self." + name + " = " + name)

    ast_output.append("    ")
    ast_output.append("    def accept(self, visitor : StmtVisitor):")
    ast_output.append("        return visitor.visit_" + className.lower() + "_stmt(self)")
    ast_output.append("    ")
    ast_output.append("    ")

##### HEADER #####
ast_output.append("from abc import ABC, abstractmethod")
ast_output.append("import expr as Expr")
ast_output.append("from tokens import Token")
ast_output.append("")
ast_output.append("")

ast_output.append("### STMT ABSTRACT CLASS ###")
ast_output.append("class Stmt(ABC):")
ast_output.append("    def __init__(self):")
ast_output.append("         raise NotImplementedError")
ast_output.append("")
ast_output.append("    @abstractmethod")
ast_output.append("    def accept(self, visitor : StmtVisitor):")
ast_output.append("        raise NotImplementedError")
ast_output.append("")
ast_output.append("")

##### GENERATING STATEMENT VISITOR #####
ast_output.append("### STMT VISITOR ABSTRACT CLASS ###")
ast_output.append("class StmtVisitor(ABC):")
for rule in RULES:
    className = rule.split("=")[0].strip()
    ast_output.append("    @abstractmethod")
    ast_output.append("    def visit_" + className.lower() + "_stmt(self, stmt : " + className + "):")
    ast_output.append("        raise NotImplementedError")
    ast_output.append("")

for rule in RULES:
    className = rule.split("=")[0].strip()
    fieldList = rule.split("=")[1].strip()

ast_output.append("")

##### GENERATING STATEMENT CLASSES #####
ast_output.append("### STATEMENTS ###")
for rule in RULES:
    className = rule.split("=")[0].strip()
    fieldList = rule.split("=")[1].strip()

    define_rule(className, fieldList)

with open(ast_path, 'x') as file:
    file.write('\n'.join(ast_output))