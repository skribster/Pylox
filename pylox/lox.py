from pathlib import Path

from scanner import Scanner
from parser import Parser
from resolver import Resolver
from interpreter import Interpreter
from expr import Expr


COMMANDS = {
    'exit' : exit,
}


class Lox:
    interpreter = Interpreter()

    @staticmethod
    def usage():
        print("Usage: lox [file]")
        exit(64)

    @staticmethod
    def run_file(path : str) -> None:
        with open(path, mode='r', encoding='utf-8') as file:
            Lox.run(file.read())
    
    @staticmethod
    def run_prompt() -> None:
        while True:
            source = input('> ')
            if source in COMMANDS:
                COMMANDS[source]()
                continue

            scanner = Scanner(source)
            tokens = scanner.scan_tokens()
            

            parser = Parser(tokens)
            syntax = parser.parse_repl()
            if syntax is None:
                return
            
            if isinstance(syntax, list):
                Lox.interpreter.interpret(syntax)
            
            elif isinstance(syntax, Expr):
                result = Lox.interpreter.interpret(syntax)
                if result is not None:
                    print("= " + Interpreter.stringify(result))
                        
    @staticmethod
    def run(source : str) -> None:
        scanner = Scanner(source)
        tokens = scanner.scan_tokens()

        parser = Parser(tokens)
        statements = parser.parse()
        if statements is None:
            return
        
        resolver = Resolver(Lox.interpreter)
        resolver.resolve(statements)
        Lox.interpreter.interpret(statements)


    @staticmethod
    def report(line : int, message : str) -> None:
        print(f'[line {line}] Error: {message}')

        Lox.had_error = True

    