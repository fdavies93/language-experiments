# IPL means Infix Plus Lexer

from enum import IntEnum, auto
from lexer import AbstractLexer, LexTransition, LexTransitionFn
from argparse import ArgumentParser
from sys import argv

class IPLexToken(IntEnum):
    MINUS = auto()
    OPEN_BRACKET = auto()
    CLOSE_BRACKET = auto()
    PLUS = auto()
    MULTIPLY = auto()
    DIVIDE = auto()
    NUMBER = auto()
    NEW_LINE = auto()
    ASSIGN = auto()
    TOKEN = auto()

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

def push_number(obj : AbstractLexer, next_char : str):
    obj.tokens.append( (IPLexToken.NUMBER, obj.token) )

def push_token(obj : AbstractLexer, next_char : str):
    obj.tokens.append( (IPLexToken.TOKEN, obj.token) )

def push_minus(obj : AbstractLexer, next_char : str):
    prev_token = None
    if len(obj.tokens) > 0:
        prev_token = obj.tokens[-1]
    if prev_token != None and prev_token[0] in {IPLexToken.NUMBER, IPLexToken.CLOSE_BRACKET, IPLexToken.TOKEN}:
        obj.tokens.append((IPLexToken.PLUS, '+'))
    if (len(obj.token) % 2) != 0:
        obj.tokens.append((IPLexToken.MINUS, '-'))

number_space = ( push_number, AbstractLexer.reset_token )
number_to_minus = (push_number, AbstractLexer.reset_token, AbstractLexer.accumulate)
number_tuple = ( push_number, push_operator, AbstractLexer.reset_token )

exit_minus = (push_minus, AbstractLexer.reset_token, AbstractLexer.accumulate)

token_space = ( push_token, AbstractLexer.reset_token )
token_to_minus = ( push_token, AbstractLexer.reset_token, AbstractLexer.accumulate)
token_tuple = ( push_token, push_operator, AbstractLexer.reset_token )

transitions = {
            # all we care about is:
            # do we push the current accumulator? as what?
            # do we push the next token? as what?
            
            # change this so that we supply a list of atomic functions
            # which are executed on a given transition, rather than 
            # using predefined behaviours
            # PUSH should be append token, append accumulator, reset accumulator
            # ACCUMULATE should be append token to accumulator / tape
            "neutral": [
                (r'[\t ]','neutral', ()),
                (r'[\n\r]','neutral', push_operator), # i.e. do nothing
                (r'\(','neutral', push_operator), 
                (r'[0-9]','number', AbstractLexer.accumulate),
                (r'\.','number-dot', AbstractLexer.accumulate),
                (r'-','minus', AbstractLexer.accumulate),
                (r'[A-Z]|[a-z]|_','token', AbstractLexer.accumulate),
                (r'#','comment',())
            ],
            "number": [
                (None, 'neutral', number_space),
                (r'[\n\r]','neutral', number_tuple),
                (r'[ \t]','expect-operator', number_space),
                (r'[0-9]', 'number', AbstractLexer.accumulate),
                (r'\)', 'expect-operator', number_tuple),
                (r'[+*(/=]','neutral', number_tuple),
                (r'\.','number-dot', AbstractLexer.accumulate),
                (r'-','minus', number_to_minus),
                (r'#','comment', number_space)
            ],
            'number-dot': [
                (None, 'neutral', number_space),
                (r'[\n\r]','neutral', number_tuple),
                (r'[ \t]','expect-operator', number_space),
                (r'[0-9]', 'number-dot', AbstractLexer.accumulate),
                (r'\)', 'expect-operator', number_tuple),
                (r'[+*(/=]','neutral', number_tuple),
                (r'-','minus', number_to_minus),
                (r'#','comment',number_space)
            ],
            'expect-operator': [
                # perhaps check if brackets have been closed correctly - neutral might be wrong state to go to
                (r'[\n\r]','neutral', push_operator),
                (r'[ \t]','expect-operator', ()),
                (r'[+*\(/=]','neutral', push_operator),
                (r'-','minus', AbstractLexer.accumulate),
                (r'\)','expect-operator', push_operator),
                (r'#', 'comment', ())
            ],
            'minus': [
                # newline in the middle of a minus expression is INVALID
                (r'[ \t]','minus', ()), # i.e. do nothing
                (r'-','minus', AbstractLexer.accumulate),
                (r'\.','number-dot', exit_minus),
                (r'[0-9]', 'number', exit_minus),
                (r'[A-Z]|[a-z]|_','token', exit_minus)
                # comment after minus will lead to invalid code, therefore invalid
            ],
            'comment': [
                (None, 'neutral', ()),
                (r'[\n\r]','neutral',push_operator),
                (r'(?![\n\r])','comment',())
            ],
            'token': [
                (None, 'neutral', token_space),
                (r'[\n\r]','neutral', token_tuple),
                (r'[ \t]','expect-operator', token_space),
                (r'\)', 'expect-operator', token_tuple),
                (r'[+*(/=]','neutral', token_tuple),
                (r'-','minus', token_to_minus),
                (r'[A-Z]|[a-z]|_','token', AbstractLexer.accumulate),
                (r'#','comment', token_space)

            ]
}

# just a convenient wrapper over the AbstractLexer
class InfixPlusLexer(AbstractLexer):
    def __init__(self):
        super().__init__(transitions,"neutral")

if __name__ == "__main__":
    luthor = AbstractLexer(transitions, "neutral")

    parser = ArgumentParser(prog="Infix Plus Lexer")
    parser.add_argument('-i', '--input',action='store')

    args = parser.parse_args(argv[1:])

    if args.input:
        with open(args.input,'r') as f:
            file = f.read()
        tokens = luthor.lex(file)
        print(tokens)