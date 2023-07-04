from ipl import InfixPlusLexer, IPLexToken
from enum import IntEnum, auto
from argparse import ArgumentParser
from typing import Iterable
from collections import deque
import json
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
    NULL = auto()

tokenMap = {
    IPToken.PROGRAM: "PROGRAM",
    IPToken.EXPR: "EXPR",
    IPToken.ASSIGNMENT: "ASSIGN",
    IPToken.ADD: "ADD",
    IPToken.MUL: "MUL",
    IPToken.TERM: "TERM",
    IPToken.BRACKET_EXPR: "BRACKET",
    IPToken.UNARY_EXPR: "UNARY",
    IPToken.NULL: "NULL"
}

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
                if len(expr_node[0][1]) > 0:
                    children.append(expr_node[0])
                    # print(expr_node)
                group_start = i+1
        # print(children)
        return ((IPToken.PROGRAM, children),[])

    def parse_expr(self, tokens : TokenList) -> IPTuple:
        # print(tokens)
        # if len(tokens) == 0:
        #     return ((IPToken.EXPR, []),[])

        for fn in (self.parse_assignment, self.parse_add):
            try:
                node = fn(tokens)
                return ((IPToken.EXPR, [node[0]]), node[1])
            except ValueError as err:
                print(err)
        
        # return ((IPToken.EXPR, []), [tokens])
        raise ValueError("No valid expression found.")
        
    def parse_assignment(self, tokens : TokenList) -> IPTuple:
        if len(tokens) <= 2 or tokens[1][0] != IPLexToken.ASSIGN:
            raise ValueError("Not an assignment.")
        
        if not tokens[0][0] == IPLexToken.TOKEN:
            raise ValueError("Expression looks like an assignment but isn't.")
        
        children = list(tokens[:2])
        expr = self.parse_expr(tokens[2:])
        children.append(expr[0])

        return ((IPToken.ASSIGNMENT, children), expr[1])
    
    def parse_add(self, tokens : TokenList) -> IPTuple:
        children = []
        
        # if len(tokens) == 0:
        #     raise ValueError("Invalid add expression: no tokens.")
        left_tokens = self.parse_mul(tokens)
        # print(left_tokens[1])

        children.append(left_tokens[0])

        remaining_tokens = left_tokens[1]
        # if len(remaining_tokens) == 1:
        #     raise ValueError("Invalid add expression.")
        
        if len(remaining_tokens) > 0 and remaining_tokens[0][0] in {IPLexToken.PLUS, IPLexToken.MINUS}:
            # if remaining_tokens[0][0] not in {IPLexToken.PLUS, IPLexToken.MINUS}:
            #     raise ValueError("Invalid add expression.")
            
            children.append(remaining_tokens[0])

            right_tokens = self.parse_add(remaining_tokens[1:])
            
            children.append(right_tokens[0])

            remaining_tokens = right_tokens[1]

        return ((IPToken.ADD, children), remaining_tokens)
    
    def parse_mul(self, tokens : TokenList) -> IPTuple:
        children = []
        
        # if len(tokens) == 0:
        #     raise ValueError("Invalid mul expression: length < 1")
        left_tokens = self.parse_term(tokens)

        children.append(left_tokens[0])

        remaining_tokens = left_tokens[1]
        # print(remaining_tokens)

        # if len(remaining_tokens) == 1:
        #     print(remaining_tokens)
        #     raise ValueError("Invalid mul expression: dangling operator")
        
        if len(remaining_tokens) > 0 and remaining_tokens[0][0] in {IPLexToken.MULTIPLY, IPLexToken.DIVIDE}:

            # if remaining_tokens[0][0] not in {IPLexToken.DIVIDE, IPLexToken.MULTIPLY}:
            #     raise ValueError("Invalid mul expression: not a divide or multiply expression")

            children.append(remaining_tokens[0])

            right_tokens = self.parse_mul(remaining_tokens[1:])
            
            children.append(right_tokens[0])

            remaining_tokens = right_tokens[1]

        # print(remaining_tokens)
        return ((IPToken.MUL, children), remaining_tokens)
    
    def parse_term(self, tokens : TokenList) -> IPTuple:
        if len(tokens) == 0:
            print("Token list is empty.")
            return ((IPToken.TERM, [(IPToken.NULL, "")]), [])

        first = tokens[0][0]

        if first in {IPLexToken.NUMBER, IPLexToken.TOKEN}:
            return ((IPToken.TERM, [tokens[0]]), tokens[1:])
                
        for fn in (self.bracket_expr, self.unary_expr):
            try:
                node = fn(tokens)
                return ((IPToken.TERM, [node[0]]), node[1])
            except ValueError as err:
                # print(tokens)
                print(err)

        return ((IPToken.TERM, [(IPToken.NULL, "")]), tokens)
        # raise ValueError("No valid term found.")

    def bracket_expr(self, tokens : TokenList) -> IPTuple:
        # check opening bracket
        if not tokens[0][0] == IPLexToken.OPEN_BRACKET or len(tokens) < 2:
            raise ValueError("Not a bracket expression: incorrect brackets.")
        
        expr = self.parse_expr(tokens[1:])

        remaining = expr[1]
        
        # check closing bracket
        if not len(remaining) > 0 or not remaining[0][0] == IPLexToken.CLOSE_BRACKET:
            # print(remaining)
            raise ValueError("Not a bracket expression.")

        children = [tokens[0], expr[0], remaining[0]]
        # print(children)

        return ((IPToken.BRACKET_EXPR, children),remaining[1:])

    def unary_expr(self, tokens : TokenList) -> IPTuple:
        # using set to allow for adding more unaries later
        if len(tokens) < 2 or not tokens[0][0] in {IPLexToken.NEGATE}:
            raise ValueError("Invalid unary expression.")
        
        unary = tokens[0]
        expr = self.parse_term(tokens[1:])

        children = [unary, expr[0]]

        return ((IPToken.UNARY_EXPR, children), expr[1])

    def parse(self, tokens):
        return self.parse_program(tokens)
    
    def prune(self, root : IPNode):
        # eliminate nodes which resolve to empty expressions
        children = []
        tokens = 0
        # print(root[0])
        for child in root[1]:
            child_tokens = 0
            
            if isinstance(child[0],IPLexToken):
                child_tokens = 1
                children.append(child)
            
            else:
                pruned_child = self.prune(child)
                child_tokens += pruned_child[1]
            
                if child_tokens > 0:
                    children.append(pruned_child)

            tokens += child_tokens

        print(f"😎 {root[1]}")

        new_node = (root[0], children)

        return (new_node, tokens)
    
    def viz_node(self, node : IPNode) -> list[str]:
        # print(node)

        num = 0
        lines = []
        nodes = deque((node,))
        # print(nodes)
        while len(nodes) > 0:
            cur = nodes.popleft()
            # print(cur)
            if isinstance(cur[0], IPToken):
                label = tokenMap.get(cur[0])
            elif isinstance(cur[0], IPLexToken):
                label = cur[1]

            lines.extend(
                [
                    f'n{num} ;',
                    f'n{num} [label="{label}"] ;',
                ]
            )
            if isinstance(cur[0], IPLexToken):
                num += 1
                continue

            for child in cur[1]:
                nodes.append(child)
                child_num = num+len(nodes)
                lines.extend([
                    f"n{child_num} ;",
                    f"n{num} -- n{child_num} ;"
                ])
            num += 1
        return lines

    def graphviz(self, node : IPNode, outPath : str):
        lines = [
            'graph fsm {',
            'fontname="Roboto,Arial,sans-serif"',
            'node [fontname="Roboto,Arial,sans-serif"]',
            'node [shape=circle];'
        ]
        nodes = self.viz_node(node)
        print(nodes)
        lines.extend(nodes)
        lines.append('}')

        with open(outPath, "w") as f:
            for ln in lines:
                f.write(f"{ln}\n")
        

def parse_file(path):
    luthor = InfixPlusLexer()
    kal_el = InfixPlusParser()
    
    with open(path,'r') as f:
        file = f.read()
    
    tokens = luthor.lex(file)
    parse_tree = kal_el.parse(tokens)[0]

    kal_el.graphviz(parse_tree, "parse-tree.gv")
    # print(parse_tree)
    # ast = kal_el.prune(parse_tree)
    return parse_tree

def test_term_blank(lexer,parser : InfixPlusParser):
    token = parser.parse_term([])
    print(token)

def test_term_close(lexer,parser : InfixPlusParser):
    lex_tok = [
        (IPLexToken.CLOSE_BRACKET,")")
    ]
    token = parser.parse_term(lex_tok)
    print(token)

def test_term_complex(lexer,parser : InfixPlusParser):
    lex_tok = [
        (IPLexToken.NUMBER,"10"),
        (IPLexToken.CLOSE_BRACKET,")")
    ]
    token = parser.parse_term(lex_tok)
    print(token)

def test_mul_term_only(lexer, parser : InfixPlusParser):
    lex_tok = [
        (IPLexToken.NUMBER,"10"),
        (IPLexToken.CLOSE_BRACKET,")")
    ]
    token = parser.parse_mul(lex_tok)
    print(token)

def test_mul_norm(lexer, parser : InfixPlusParser):
    lex_tok = [
        (IPLexToken.NUMBER,"10"),
        (IPLexToken.MULTIPLY,"*"),
        (IPLexToken.NUMBER,"10")
    ]
    token = parser.parse_mul(lex_tok)
    print(token)

def run_tests():
    luthor = InfixPlusLexer()
    kal_el = InfixPlusParser()
    tests = (
        test_term_blank,
        test_term_close,
        test_term_complex,
        test_mul_term_only,
        test_mul_norm
    )
    
    for test in tests:
        try:
            print(f"🔥 {test.__name__} 🔥")
            test(luthor, kal_el)
            luthor.reset()
        except ValueError as err:
            print(err)



if __name__ == "__main__":
    

    arg_parser = ArgumentParser(prog="Infix Plus Lexer")
    arg_parser.add_argument('-i', '--input',action='store')
    # arg_parser.add_argument('-v', '--viz',action='store')
    arg_parser.add_argument('-t', '--test',action='store_true')

    args = arg_parser.parse_args(sys.argv[1:])

    if args.input:
        parsed = parse_file(args.input)
    elif args.test:
        run_tests()