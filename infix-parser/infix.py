from enum import IntEnum
from dataclasses import dataclass, asdict
from copy import deepcopy
from typing import Callable, Union
from json import dumps
from io import TextIOWrapper

digits = [chr(i) for i in range(48,58)] # digits by char code
whitespace = [' ', '\n', '\r', '\t'] # ignore
open_bracket = '('
close_bracket = ')'
adme = ['+', '^', '/', '*']
minus = '-'
dot = '.'

operators = [open_bracket, close_bracket, minus]
operators.extend(adme)

class InfixLexer:
    def __init__(self):
        self.reset()

    def reset(self):
        self.tape = ""
        self.tokens = []
        self.cur_token = ""
        self.step_fn = self.step_neutral
        # could be removed to a second pass
        self.has_dot = False
        self.brackets_open = 0
        self.prev_token = None

    def step_neutral(self):
        next_char = self.tape[0]
        self.tape = self.tape[1:]

        if next_char in digits or next_char == dot:
                # it's a number
                self.cur_token = next_char
                self.step_fn = self.step_lexing_number
        elif next_char == open_bracket:
            # the only valid operators to start an expression are - or (
            self.tokens.append(next_char)
            self.prev_token = next_char
            self.brackets_open += 1

        elif next_char == minus:
            self.step_fn = self.step_lexing_minus

        elif next_char in whitespace:
            # it's whitespace, do nothing
            pass
        else:
            # it's invalid, throw an error
            raise ValueError
        
        if len(self.tape) == 0 and self.cur_token != "":
            self.tokens.append(self.cur_token)
            self.prev_token = self.cur_token
        
    def step_lexing_minus(self):

        minuses = 1

        next_char = self.tape[0]
        self.tape = self.tape[1:]

        while (next_char == '-' or next_char in whitespace) and len(self.tape) > 0:
            if next_char == '-':
                minuses += 1
            next_char = self.tape[0]
            self.tape = self.tape[1:]
        
        # this should properly be a second lexing step
        if self.prev_token not in {None, open_bracket}.union(adme):
            self.tokens.append('+')
            self.prev_token = '+'
            # if it WASN'T in that set then + is valid, so add it as an operator

        if not (minuses % 2) == 0:
            self.tokens.append('-')
            self.prev_token = '-'
        # to here

        # this is identical to step_neutral_fn - move to own fn?
        if next_char in digits or next_char == dot:
            self.cur_token = next_char
            self.step_fn = self.step_lexing_number

        elif next_char == open_bracket:
            # the only valid operators to start an expression are - or (
            self.tokens.append(next_char)
            self.prev_token = next_char
            self.brackets_open += 1
            self.step_fn = self.step_neutral
        else:
            raise ValueError()
        
        if len(self.tape) == 0 and self.cur_token != "":
            self.tokens.append(self.cur_token)
            self.prev_token = self.cur_token
        # end function step_neutral
        

    def step_lexing_number(self):
        next_char = self.tape[0]
        self.tape = self.tape[1:]

        if next_char in digits:
            self.cur_token += next_char

        elif next_char == dot and not self.has_dot:
            self.has_dot = True
            self.cur_token += next_char

        elif next_char in operators:
            self.has_dot = False

            self.tokens.append(self.cur_token)
            self.prev_token = self.cur_token

            self.cur_token = ""

            if next_char == minus:
                self.step_fn = self.step_lexing_minus
                return

            self.tokens.append(next_char)
            self.prev_token = next_char

            self.step_fn = self.step_neutral
            
            if next_char == close_bracket:
                self.brackets_open -= 1
                self.step_fn = self.step_expect_operator

        elif next_char in whitespace:
            pass
        
        else:
            raise ValueError
        
        if len(self.tape) == 0 and self.cur_token != "":
            self.tokens.append(self.cur_token)
            self.prev_token = self.cur_token

    def step_expect_operator(self):
        next_char = self.tape[0]
        self.tape = self.tape[1:]

        if next_char in operators:
            if next_char == close_bracket:
                self.brackets_open -= 1
            
            elif next_char == minus:
                self.step_fn = self.step_lexing_minus
                return

            self.tokens.append(next_char)
            self.prev_token = next_char
        
            if not next_char == close_bracket:
                self.step_fn = self.step_neutral

        elif next_char in whitespace:
            return
        else:
            raise ValueError

    def lex(self, input : str):
        self.reset()
        self.tape = input

        while len(self.tape) > 0:
            self.step_fn()
        
        if self.brackets_open != 0:
            raise ValueError("Mismatched brackets in expression.")

        return self.tokens

@dataclass
class ParseNode():
    token : str
    children : list["ParseNode"]

    def __eq__(self, other):
        if isinstance(other, ParseNode) and other.token == self.token:
            return True
        elif isinstance(other, str) and other == self.token:
            return True
        
        return False

class InfixParser():

    # run through each parsing step in turn, by the same process
    # bracketise
    # identify and simplify unary minus
    # multiply
    # divide
    # add (therefore, also subtract)

    def __init__(self):
        self.operations = [
            InfixParser.parse_unary_minus,
            lambda ls : InfixParser.pbo("^", ls),
            lambda ls : InfixParser.pbo("*", ls),
            lambda ls : InfixParser.pbo("/", ls),
            lambda ls : InfixParser.pbo("+", ls),
        ]

    @classmethod
    def parse_unary_minus(cls, tokens: list[Union[str, ParseNode]]) -> list[Union[str, ParseNode]]:
        i = 0
        out_list = []
        while i < len(tokens):
            if tokens[i] == '-':
                out_list.append(ParseNode('-', [tokens[i+1]]))
                i += 1 # so that we step forward TWO
            else:
                out_list.append(tokens[i])
            i += 1
        return out_list

    # pbo stands for Parse Binary Operator
    @classmethod
    def pbo(cls, operator : str, tokens: list[Union[str, ParseNode]]) -> list[Union[str, ParseNode]]:
        i = 0
        out_list = deepcopy(tokens)
        while i < len(out_list):
            if out_list[i] == operator and isinstance(out_list[i],str):
                new_list : list = out_list[:i-1]
                new_list.append(ParseNode(operator, [out_list[i-1], out_list[i+1]]))
                new_list.extend(out_list[i+2:])
                out_list = new_list
                i = 0
            i += 1
        return out_list

    # should return the root of an AST
    def parse(self, tokens : list[str]) -> ParseNode:
        if len(tokens) == 0:
            return None
        # bracketise, then do other operations

        cur_list : list = deepcopy(tokens)
        inner = None

        cur_i = 0
        while cur_i < len(cur_list):
            token = cur_list[cur_i]
            if token == '(':
                # recurse, using list after bracket
                inner = self.parse( cur_list[cur_i + 1 :] )
                cur_list = cur_list[ : cur_i]
                cur_list.extend(inner)
                cur_i = 0

            elif token == ")":
                # we've reached the innermost statement of expression
                # take the whole expression and parse it according to
                # operator precedence
                out_list = cur_list[: cur_i]

                for operation in self.operations:
                    out_list = operation(out_list)

                out_list.extend( cur_list[cur_i + 1 :] )

                return out_list
            
            else: cur_i += 1

        for operation in self.operations:
            cur_list = operation(cur_list)

        return cur_list[0]

def evaluate(node):
    ops = {
        '^' : lambda x, y : x ** y,
        '+' : lambda x, y : x + y,
        '/' : lambda x, y : x / y,
        '*' : lambda x, y : x * y
    }
    if isinstance(node, str):
        return float(node)
    elif isinstance(node, ParseNode):
        if node.token in adme:
            left = evaluate(node.children[0])
            right = evaluate(node.children[1])
            return ops[node.token](left, right)
        elif node.token == minus:
            return evaluate(node.children[0]) * -1



def op_to_llvm(op, children : tuple[Union[int, float]], new_register : int):
    
    # determine if left is number or register
    left_arg = f"{children[0]}"
    if isinstance(children[0], int):
        left_arg = "%" + left_arg

    # determine if right is number or register
    if op == minus:
        right_arg = "-1.0"
    else:
        right_arg = f"{children[1]}"
        if isinstance(children[1], int):
            right_arg = "%" + right_arg

    llvm_ops = {
        '+': 'fadd',
        '-': 'fmul',
        '/': 'fdiv',
        '*': 'fmul'
    }

    return f"%{new_register} = {llvm_ops[op]} float {left_arg}, {right_arg}\n"

def compile_at(node, handle : TextIOWrapper, prev_node = -1):
    if isinstance(node, str):
        return float(node)
    elif isinstance(node, ParseNode):
        if node.token in adme:
            left = compile_at(node.children[0], handle, prev_node=prev_node)
            left_r = left
            
            if isinstance(left, float):
                left_r = prev_node

            if node.token == minus:
                handle.write( op_to_llvm(minus, (left), left_r + 1) )
                return left_r + 1

            right = compile_at(node.children[1], handle, prev_node=left_r)

            register = right

            if isinstance(right, float):
                register = left_r

            handle.write( op_to_llvm(node.token, (left, right), register + 1) )
            return register + 1

def compile(node, path):
    prefix = '\n'.join([
        "@.str = private unnamed_addr constant [3 x i8] c\"%f\\00\", align 1",
        "declare i32 @printf(i8*, ...)",
        "define i32 @main() {",
        "entry:",
        ""
    ])
    with open(path, "w") as f:
        f.write(prefix)
        last_node = compile_at(node, f)

        suffix = '\n'.join([
            f"%{last_node+1} = fpext float %{last_node} to double",
            f"%out = call i32 (i8*, ...) @printf(i8* getelementptr inbounds ([3 x i8], [3 x i8]* @.str, i64 0, i64 0), double %{last_node+1})",
            "ret i32 0",
            "}"
        ])
        f.write(suffix)
