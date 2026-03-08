import expr as Expr


class AstPrinter(Expr.ExprVisitor):
    def __init__(self):
        pass

    def print(self, expr : Expr.Expr):
        return expr.accept(self)
    
    def parenthesize(self, name : str, *expressions : Expr.Expr) -> str:
        out = "(" + name

        for expr in expressions:
            out += " "
            out += expr.accept(self)

        out += ")"
        return out

    # (left expr) (operator) (right expr) -> 5 + 3 | 3 == 4 | a <= 3
    def visit_binary_expr(self, expr : Expr.Binary):
        return self.parenthesize(expr.operator.lexeme, expr.left, expr.right)
    
    # (operator) (right expr) -> -5 | !true 
    def visit_grouping_expr(self, expr : Expr.Grouping):
        return self.parenthesize("group", expr.expression)

    def visit_literal_expr(self, expr : Expr.Literal):
        if (expr.value is None): return "nil"
        return str(expr.value)
    
    def visit_unary_expr(self, expr : Expr.Unary):
        return self.parenthesize(expr.operator.lexeme, expr.right)