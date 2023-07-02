from ipl import InfixPlusLexer, IPLexToken
from enum import IntEnum, auto
from argparse import ArgumentParser
from typing import Iterable
import sys

class IPToken(IntEnum):
    PROGRAM = auto()
    EXPR = auto()
    ASSIGNMENT = auto()
    ADD = auto()
    MUL = auto()
    TERM = auto()

IPNode = tuple[IPToken,list["IPNode"]]
TokenList = Iterable[tuple[IPLexToken, str]]

class InfixPlusParser():

    def pattern_match(self, tokens : TokenList, pattern : Iterable[IPLexToken]):
        if len(tokens) != len(pattern):
            return False
        for i, token in enumerate(tokens):
            if token[0] != pattern[i]:
                return False
        return True

    def parse_program(self, tokens : TokenList) -> IPNode:
        # needs to be rewritten to correctly consume tokens
        # and nest expressions
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

    def parse_expr(self, tokens : TokenList) -> IPNode:
        for fn in (self.parse_assignment, self.parse_add):
            try:
                node = fn(tokens)
                return ((IPToken.EXPR, node[0]), node[1])
            except ValueError:
                pass
        raise ValueError
        
    def parse_assignment(self, tokens : TokenList) -> IPNode:
        if len(tokens) > 2 and tokens[1][0] == IPLexToken.ASSIGN:
            if not tokens[0][0] == IPLexToken.TOKEN:
                raise ValueError("Expression looks like an assignment but isn't.")
            return (IPToken.ASSIGNMENT, self.parse_expr(tokens[2:]), )
        raise ValueError("Not an assignment.")

    def parse_add(self, tokens : TokenList) -> tuple[IPNode,list[IPLexToken]]:
        children = []
        
        if len(tokens) == 0:
            raise ValueError("Invalid add expression.")
        left_tokens = self.parse_mul(tokens)

        children.append(left_tokens[0])

        remaining_tokens = left_tokens[1]
        if len(remaining_tokens) == 1:
            raise ValueError("Invalid add expression.")
        
        if len(remaining_tokens) > 0:
            if remaining_tokens[0][0] not in {IPLexToken.PLUS, IPLexToken.MINUS}:
                raise ValueError("Invalid add expression.")
            
            children.append(remaining_tokens[0])

            right_tokens = self.parse_add(remaining_tokens[1:])
            
            children.append(right_tokens[0])

            remaining_tokens = right_tokens[1]

        return ((IPToken.ADD, children), remaining_tokens)
    
    def parse_mul(self, tokens : TokenList) -> tuple[IPNode,list[IPLexToken]]:
        children = []
        
        if len(tokens) == 0:
            raise ValueError("Invalid mul expression.")
        left_tokens = self.parse_term(tokens)

        children.append(left_tokens[0])

        remaining_tokens = left_tokens[1]

        if len(remaining_tokens) == 1:
            raise ValueError("Invalid mul expression.")
        
        if len(remaining_tokens > 0):

            if remaining_tokens[0][0] not in {IPLexToken.DIVIDE, IPLexToken.MULTIPLY}:
                raise ValueError("Invalid mul expression.")

            children.append(remaining_tokens[0])

            right_tokens = self.parse_mul(remaining_tokens[1:])
            
            children.append(right_tokens[0])

            remaining_tokens = right_tokens[1]

        return ((IPToken.MUL, children), remaining_tokens)
    
    def parse_term(self, tokens : TokenList) -> tuple[IPNode, list[IPLexToken]]:
        for lex_type in (IPLexToken.NUMBER, IPLexToken.TOKEN):
            if tokens[0][0] == lex_type:
                return ((IPToken.TERM, tokens[0]), tokens[1:])
        
        for fn in (self.bracket_expr, self.unary_expr):
            try:
                node = fn(tokens)
                return ((IPToken.TERM, node[0]), node[1])
            except ValueError:
                pass
        raise ValueError("No valid term found.")

    def bracket_expr(self, tokens : TokenList):
        if not tokens[0][0] == IPLexToken.OPEN_BRACKET or len(tokens) < 2:
            raise ValueError("Not a bracket expression.")
        
        expr = self.parse_expr(tokens[1:])

        if not len(expr[1]) > 0 or :


    def unary_expr(self, tokens : TokenList):
        pass

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