from typing import Any

from errors import ScanError
from tokens import (
    Token, 
    TokenType as TT,
    KEYWORDS,
)


class Scanner:
    def __init__(self, source : str):
        self.source = source
        self.tokens = []

        self.start = 0
        self.current = 0
        self.line = 1

    def scan_tokens(self) -> list[Token]:
        while not self.is_at_end():
            self.start = self.current
            self.scan_token()

        self.tokens.append(Token(TT.EOF, "", None, self.line))

        return self.tokens

    def scan_token(self):
        character = self.advance()
        match character:
            case '(': self.add_token(TT.LEFT_PAREN)
            case ')': self.add_token(TT.RIGHT_PAREN)
            case '{': self.add_token(TT.LEFT_BRACE)
            case '}': self.add_token(TT.RIGHT_BRACE)
            case ',': self.add_token(TT.COMMA)
            case '.': self.add_token(TT.DOT)
            case '-': self.add_token(TT.MINUS)
            case '+': self.add_token(TT.PLUS)
            case ';': self.add_token(TT.SEMICOLON)
            case '*': self.add_token(TT.STAR)
            case '!':
                token = TT.BANG_EQUAL if self.match('=') else TT.BANG
                self.add_token(token)
            case '=':
                token = TT.EQUAL_EQUAL if self.match('=') else TT.EQUAL
                self.add_token(token)
            case '<':
                token = TT.LESS_EQUAL if self.match('=') else TT.LESS
                self.add_token(token)   
            case '>':
                token = TT.GREATER_EQUAL if self.match('=') else TT.GREATER
                self.add_token(token)
            
            case '/':
                if self.match('/'):
                    self.single_line_comment()
                elif self.match('*'):
                    self.multi_line_comment()
                else:
                    self.add_token(TT.SLASH)

            case ' ' | '\r' | '\t':
                # Ignore whitespace.
                pass

            case '\n':
                self.line += 1

            case '"':
                self.string_token()

            case _: 
                if self.is_digit(character):
                    self.number_token()
                elif self.is_alpha(character):
                    self.identifier()
                else:
                    raise ScanError(self.line, "Unexpected character.")  

    def single_line_comment(self):
        # A comment goes until the end of the line.
        while self.peek() != '\n' and not self.is_at_end():
            self.advance()

    def multi_line_comment(self):
        depth = 1

        while depth != 0:
            if self.is_at_end():
                raise ScanError(self.line, "Unterminated block comment.")
            
            elif self.peek() == "*" and self.peek_next() == "/":
                depth -= 1
                self.advance()
                self.advance()

            elif self.peek() == "/" and self.peek_next() == "*":
                depth += 1
                self.advance()
                self.advance()

            else:
                if self.peek() == '\n':
                    self.line += 1

                self.advance()

    def string_token(self):
        while self.peek() != '"' and not self.is_at_end():
            if self.peek() == '\n': self.line += 1
            self.advance()

        if self.is_at_end():
            raise ScanError(self.line, "Unterminated string.")
            return

        # Consume ending ".        
        self.advance()

        # Trim the surrounding quotes.
        value = self.source[self.start + 1 : self.current - 1]
        self.add_token(TT.STRING, value)

    def number_token(self):
        # Consume the numbers on the left side of the decimal.
        while self.is_digit(self.peek()):
            self.advance()

        # Look for fractional part (e.x. ".4" or ".3")
        if self.peek() == '.' and self.is_digit(self.peek_next()):
            # Consume the "."
            self.advance() 

            # Consume the numbers on the right side of the decimal.
            while self.is_digit(self.peek()): self.advance()

        text = self.source[self.start : self.current]
        self.add_token(TT.NUMBER, float(text))

    def identifier(self):
        while self.is_alphanumeric(self.peek()):
            self.advance()

        text = self.source[self.start : self.current]
        type : TT = KEYWORDS.get(text) or TT.IDENTIFIER
        self.add_token(type)

    # HEPLER FUNCTIONS
    def add_token(self, type : TT, literal : Any = None):
        text = self.source[self.start : self.current]
        token = Token(type, text, literal, self.line)
        self.tokens.append(token)

    def is_at_end(self) -> bool:
        return self.current >= len(self.source)
    
    def advance(self) -> str:
        self.current += 1
        return self.source[self.current - 1]

    def match(self, expected : str) -> bool:
        if self.is_at_end():
            return False
        
        if self.source[self.current] != expected:
            return False
        
        self.advance()
        return True

    def peek(self) -> str:
        if self.is_at_end():
            return '\0'

        next_character = self.source[self.current]
        return next_character
    
    def peek_next(self):
        if self.current + 1 >= len(self.source):
            return '\0'

        return self.source[self.current + 1] 
    
    def is_digit(self, character : str):
        return character >= '0' and character <= '9'

    def is_alpha(self, character : str):
        return  (character >= 'a' and character <= 'z') or \
                (character >= 'A' and character <= 'Z') or \
                character == '_'

    def is_alphanumeric(self, character : str):
        return self.is_alpha(character) or self.is_digit(character)