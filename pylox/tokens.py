from enum import Enum

class TokenType(Enum):
    LEFT_PAREN      = '(',
    RIGHT_PAREN     = ')',
    LEFT_BRACE      = '{',
    RIGHT_BRACE     = '}',
    COMMA           = ',',
    DOT             = '.',
    MINUS           = '-',
    PLUS            = '+',
    SEMICOLON       = ';',
    SLASH           = '/',
    STAR            = '*',

    # One or two character tokens.
    BANG            = '!', 
    BANG_EQUAL      = '!=',
    EQUAL           = '=', 
    EQUAL_EQUAL     = '==',
    GREATER         = '>', 
    GREATER_EQUAL   = '>=',
    LESS            = '<', 
    LESS_EQUAL      = '<=',

    # Literals.
    IDENTIFIER      = 'identifier', 
    STRING          = 'str', 
    NUMBER          = 'num',

    # Keywords.
    AND             = 'and', 
    CLASS           = 'class', 
    ELSE            = 'else', 
    FALSE           = 'false', 
    FUN             = 'fun', 
    FOR             = 'for', 
    IF              = 'if', 
    NIL             = 'nil', 
    OR              = 'or',
    PRINT           = 'print', 
    RETURN          = 'return', 
    SUPER           = 'super', 
    THIS            = 'this', 
    TRUE            = 'true', 
    VAR             = 'var', 
    WHILE           = 'while',
    BREAK           = 'break',
    CONTINUE        = 'continue',
    
    EOF             = ''


KEYWORDS = {
    "and"       : TokenType.AND,
    "class"     : TokenType.CLASS,
    "else"      : TokenType.ELSE,
    "false"     : TokenType.FALSE,
    "for"       : TokenType.FOR,
    "fun"       : TokenType.FUN,
    "if"        : TokenType.IF,
    "nil"       : TokenType.NIL,
    "or"        : TokenType.OR,
    "print"     : TokenType.PRINT,
    "return"    : TokenType.RETURN,
    "super"     : TokenType.SUPER,
    "this"      : TokenType.THIS,
    "true"      : TokenType.TRUE,
    "var"       : TokenType.VAR,
    "while"     : TokenType.WHILE,
    "break"     : TokenType.BREAK,
    "continue"  : TokenType.CONTINUE
}


class Token:
    def __init__(self, type : TokenType, lexeme : str, literal : object, line : int) -> None:
        self.type = type
        self.lexeme = lexeme

        if isinstance(literal, int):
            literal = float(literal)

        self.literal = literal
        self.line = line

    def __str__(self) -> str:
        return f"{self.type} : {self.lexeme} : {self.literal}"