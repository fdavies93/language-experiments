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
    BRACKET_EXPR = auto()
    UNARY_EXPR = auto()

IPNode = tuple[IPToken,list["IPNode"]]
IPTuple = tuple[IPNode,list[IPLexToken]]
TokenList = Iterable[tuple[IPLexToken, str]]

class InfixPlusParser():

    def pattern_match(self, tokens : TokenList, pattern : Iterable[IPLexToken]):
        if len(tokens) != len(pattern):
            return False
        for i, token in enumerate(tokens):
            if token[0] != pattern[i]:
                return False
        return True

    def parse_program(self, tokens : TokenList) -> IPTuple:
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
        return ((IPToken.PROGRAM, children),[])

    def parse_expr(self, tokens : TokenList) -> IPTuple:
        for fn in (self.parse_assignment, self.parse_add):
            try:
                node = fn(tokens)
                return ((IPToken.EXPR, node[0]), node[1])
            except ValueError:
                pass
        raise ValueError
        
    def parse_assignment(self, tokens : TokenList) -> IPTuple:
        if len(tokens) > 2 and tokens[1][0] == IPLexToken.ASSIGN:
            if not tokens[0][0] == IPLexToken.TOKEN:
                raise ValueError("Expression looks like an assignment but isn't.")
            return (IPToken.ASSIGNMENT, self.parse_expr(tokens[2:]), )
        raise ValueError("Not an assignment.")

    def parse_add(self, tokens : TokenList) -> IPTuple:
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
    
    def parse_mul(self, tokens : TokenList) -> IPTuple:
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
    
    def parse_term(self, tokens : TokenList) -> IPTuple:
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

    def bracket_expr(self, tokens : TokenList) -> IPTuple:
        # check opening bracket
        if not tokens[0][0] == IPLexToken.OPEN_BRACKET or len(tokens) < 2:
            raise ValueError("Not a bracket expression.")
        
        expr = self.parse_expr(tokens[1:])

        remaining = expr[1]
        
        # check closing bracket
        if not len(remaining) > 0 or not remaining[0] == IPLexToken.CLOSE_BRACKET:
            raise ValueError("Not a bracket expression.")

        children = [IPLexToken.OPEN_BRACKET, expr[0], IPLexToken.CLOSE_BRACKET]

        return ((IPToken.BRACKET_EXPR, children),remaining[1:])

    def unary_expr(self, tokens : TokenList) -> IPTuple:
        # using set to allow for adding more unaries later
        if len(tokens) < 2 or not tokens[0][0] in {IPLexToken.NEGATE}:
            raise ValueError("Invalid unary expression.")
        
        unary = tokens[0]
        expr = self.parse_expr(tokens[1:])

        children = [expr[0]]

        return ((IPToken.UNARY_EXPR, children), expr[1])

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