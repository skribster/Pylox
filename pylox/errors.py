from tokens import Token


class ScanError(Exception):
    def __init__(self, line : int, message : str):
        super().__init__(message)

        self.line = line
    
    def __str__(self):
        return f'[line {self.line}] Error: {self.message}'


class ParseError(Exception):
    def __init__(self, token : Token, message : str):
        super().__init__(message)
        self.message = message
        self.token = token

    def __str__(self):
        where = "at '" + self.token.lexeme + "'"
        return "[line " + str(self.token.line) + "] Parse error " + where + ": " + self.message
    

class ResolverError(Exception):
    def __init__(self, token : Token, message : str):
        super().__init__(message)
        self.token = token
        self.message = message


    def __str__(self):
        where = "at '" + self.token.lexeme + "'"
        return "[line " + str(self.token.line) + "] Resolver error " + where + ": " + self.message


class InterpreterError(Exception):
    def __init__(self, token : Token, message : str):
        super().__init__(message)
        self.token = token
        self.message = message


    def __str__(self):
        where = "at '" + self.token.lexeme + "'"
        return "[line " + str(self.token.line) + "] Runtime error " + where + ": " + self.message