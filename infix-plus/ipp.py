from ipl import InfixPlusLexer, IPLexToken
from enum import IntEnum, auto
from argparse import ArgumentParser
import sys

class IPToken(IntEnum):
    PROGRAM = auto()
    EXPR = auto()
    ASSIGNMENT = auto()
    ADD = auto()

IPNode = tuple[IPToken,list["IPNode"]]
TokenList = list[tuple[IPLexToken, str]]

class InfixPlusParser():

    def parse_program(self, tokens : TokenList):
        group_start = 0
        children = []
        for i, token in enumerate(tokens):
            if token[0] in {IPLexToken.EOF, IPLexToken.NEW_LINE}:
                expr_node = self.parse_expr(tokens[group_start:i])
                if len(expr_node[1]) > 0:
                    children.append(expr_node)
                    # print(expr_node)
                group_start = i+1
        print(children)
        return (IPToken.PROGRAM, children)

    def parse_expr(self, tokens : TokenList):
        for fn in (self.parse_assignment, self.parse_add):
            try:
                node = fn(tokens)
                return (IPToken.EXPR, node)
            except ValueError:
                pass
        raise ValueError
        
    def parse_assignment(self, tokens : TokenList):
        if len(tokens) > 2 and tokens[1][0] == IPLexToken.ASSIGN:
            if not tokens[0][0] == IPLexToken.TOKEN:
                raise ValueError("Expression looks like an assignment but isn't.")
            return (IPToken.ASSIGNMENT, self.parse_expr(tokens[2:]))
        raise ValueError("Not an assignment.")

    def parse_add(self, tokens : TokenList):
        return (IPToken.ADD, [])

    def parse(self, tokens):
        return self.parse_program(tokens)
    
if __name__ == "__main__":
    luthor = InfixPlusLexer()
    kal_el = InfixPlusParser()

    arg_parser = ArgumentParser(prog="Infix Plus Lexer")
    arg_parser.add_argument('-i', '--input',action='store')

    args = arg_parser.parse_args(sys.argv[1:])

    if args.input:
        with open(args.input,'r') as f:
            file = f.read()
        tokens = luthor.lex(file)
        ast = kal_el.parse(tokens)