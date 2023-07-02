# IPL means Infix Plus Lexer

from enum import IntEnum, auto
from argparse import ArgumentParser
import sys

sys.path.insert(1,"../abstract-lexer")

from lexer import AbstractLexer, LexTransition, LexTransitionFn

class IPLexToken(IntEnum):
    MINUS = auto()
    NEGATE = auto()
    OPEN_BRACKET = auto()
    CLOSE_BRACKET = auto()
    PLUS = auto()
    MULTIPLY = auto()
    DIVIDE = auto()
    NUMBER = auto()
    NEW_LINE = auto()
    ASSIGN = auto()
    TOKEN = auto()
    EOF = auto()

# you can write a bespoke function which takes the content of the token
# and emits the correct thing

op_codes = {
    '-': IPLexToken.MINUS,
    '(': IPLexToken.OPEN_BRACKET,
    ')': IPLexToken.CLOSE_BRACKET,
    '+': IPLexToken.PLUS,
    '*': IPLexToken.MULTIPLY,
    '/': IPLexToken.DIVIDE,
    '\n': IPLexToken.NEW_LINE,
    '\r': IPLexToken.NEW_LINE,
    '=': IPLexToken.ASSIGN
}

def push_operator(obj : AbstractLexer, next_char : str):
    obj.tokens.append( (op_codes[next_char], next_char) )

def push_eof(obj : AbstractLexer, next_char : str):
    obj.tokens.append( (IPLexToken.EOF, next_char) )

def push_number(obj : AbstractLexer, next_char : str):
    obj.tokens.append( (IPLexToken.NUMBER, obj.token) )

def push_token(obj : AbstractLexer, next_char : str):
    obj.tokens.append( (IPLexToken.TOKEN, obj.token) )

def push_minus(obj : AbstractLexer, next_char : str):
    prev_token = None
    if len(obj.tokens) > 0:
        prev_token = obj.tokens[-1]
    is_neg = (len(obj.token) % 2) != 0
    # two dimensions: should it be binary or unary operator?
    # if binary, should it evaluate to + or -?
    # if unary, should it evaluate to NEG or nothing?
    if prev_token != None and prev_token[0] in {IPLexToken.NUMBER, IPLexToken.CLOSE_BRACKET, IPLexToken.TOKEN}:
        if is_neg:
            obj.tokens.append((IPLexToken.MINUS, '-'))
            return
        obj.tokens.append((IPLexToken.PLUS, '+'))
    elif is_neg:
        obj.tokens.append((IPLexToken.NEGATE, '-'))

number_space = ( push_number, AbstractLexer.reset_token )
number_to_minus = (push_number, AbstractLexer.reset_token, AbstractLexer.accumulate)
number_tuple = ( push_number, push_operator, AbstractLexer.reset_token )

exit_minus = (push_minus, AbstractLexer.reset_token, AbstractLexer.accumulate)
exit_minus_bracket = (push_minus, AbstractLexer.reset_token, push_operator)

token_space = ( push_token, AbstractLexer.reset_token )
token_to_minus = ( push_token, AbstractLexer.reset_token, AbstractLexer.accumulate)
token_tuple = ( push_token, push_operator, AbstractLexer.reset_token )

transitions = {
            # start should be different to what follows operators
            # expect-expr should be a state, neutral renamed to start
            "start": [
                (None, 'start', push_eof),
                (r'[\t ]','start', ()),
                (r'[\n\r]','start', push_operator),
                (r'\(','expect-expr', push_operator),
                # (r'\)','expect-operator',push_operator),
                (r'[0-9]','number', AbstractLexer.accumulate),
                (r'\.','number-dot', AbstractLexer.accumulate),
                (r'-','minus', AbstractLexer.accumulate),
                (r'[A-Z]|[a-z]|_','token', AbstractLexer.accumulate),
                (r'#','comment',())
            ],
            "number": [
                (None, 'start', number_space + (push_eof,)),
                (r'[\n\r]','start', number_tuple),
                (r'[ \t]','expect-operator', number_space),
                (r'[0-9]', 'number', AbstractLexer.accumulate),
                (r'\)', 'expect-operator', number_tuple),
                (r'[+*(/=]','expect-expr', number_tuple),
                (r'\.','number-dot', AbstractLexer.accumulate),
                (r'-','minus', number_to_minus),
                (r'#','comment', number_space)
            ],
            'number-dot': [
                (None, 'start', number_space + (push_eof,)),
                (r'[\n\r]','start', number_tuple),
                (r'[ \t]','expect-operator', number_space),
                (r'[0-9]', 'number-dot', AbstractLexer.accumulate),
                (r'\)', 'expect-operator', number_tuple),
                (r'[+*(/=]','expect-expr', number_tuple),
                (r'-','minus', number_to_minus),
                (r'#','comment',number_space)
            ],
            # follows operators e.g. + = - * (
            'expect-expr': [
                (r'[\t ]','expect-expr', ()),
                # newline is invalid
                (r'\(','expect-expr', push_operator),
                (r'\)','expect-operator',push_operator),
                (r'[0-9]','number', AbstractLexer.accumulate),
                (r'\.','number-dot', AbstractLexer.accumulate),
                (r'-','minus', AbstractLexer.accumulate),
                (r'[A-Z]|[a-z]|_','token', AbstractLexer.accumulate)
            ],
            # always follows numbers, tokens and close brackets
            'expect-operator': [
                # perhaps check if brackets have been closed correctly - neutral might be wrong state to go to
                (r'[\n\r]','start', push_operator),
                (r'[ \t]','expect-operator', ()),
                (r'[+*\(/=]','expect-expr', push_operator),
                (r'-','minus', AbstractLexer.accumulate),
                (r'\)','expect-operator', push_operator),
                (r'#', 'comment', ())
            ],
            'minus': [
                # newline in the middle of a minus expression is INVALID
                (r'[ \t]','minus', ()), # i.e. do nothing
                (r'-','minus', AbstractLexer.accumulate),
                (r'\(','expect-expr', exit_minus_bracket), 
                (r'\.','number-dot', exit_minus),
                (r'[0-9]', 'number', exit_minus),
                (r'[A-Z]|[a-z]|_','token', exit_minus)
                # comment after minus will lead to invalid code, therefore invalid
            ],
            'comment': [
                (None, 'start', push_eof),
                (r'[\n\r]','start',push_operator),
                (r'(?![\n\r])','comment',())
            ],
            'token': [
                (None, 'start', token_space),
                (r'[\n\r]','start', token_tuple),
                (r'[ \t]','expect-operator', token_space),
                (r'\)', 'expect-operator', token_tuple),
                (r'[+*(/=]','expect-expr', token_tuple),
                (r'-','minus', token_to_minus),
                (r'[A-Z]|[a-z]|_','token', AbstractLexer.accumulate),
                (r'#','comment', token_space)

            ]
}

# just a convenient wrapper over the AbstractLexer
class InfixPlusLexer(AbstractLexer):
    def __init__(self):
        super().__init__(transitions,"start")

if __name__ == "__main__":
    luthor = AbstractLexer(transitions, "start")

    parser = ArgumentParser(prog="Infix Plus Lexer")
    parser.add_argument('-i', '--input',action='store')

    args = parser.parse_args(sys.argv[1:])

    if args.input:
        with open(args.input,'r') as f:
            file = f.read()
        tokens = luthor.lex(file)
        print(tokens)