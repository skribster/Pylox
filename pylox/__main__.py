from sys import argv

from lox import Lox


def main(args : list[str]) -> None:
    program = args.pop(0)

    if len(args) > 1:
        Lox.usage()

    elif len(argv) == 1:
        Lox.run_file(args[0])

    else:
        Lox.run_prompt()


main(argv)