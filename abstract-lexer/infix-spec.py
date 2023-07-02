from enum import IntEnum
from lexer import AbstractLexer, LexTransition, LexTransitionFn

class InfixLexTypes(IntEnum):
    MINUS = 0,
    OPEN_BRACKET = 1,
    CLOSE_BRACKET = 2,
    PLUS = 3,
    MULTIPLY = 4,
    DIVIDE = 5,
    NUMBER = 6

# you can write a bespoke function which takes the content of the token
# and emits the correct thing

op_codes = {
    '-': InfixLexTypes.MINUS,
    '(': InfixLexTypes.OPEN_BRACKET,
    ')': InfixLexTypes.CLOSE_BRACKET,
    '+': InfixLexTypes.PLUS,
    '*': InfixLexTypes.MULTIPLY,
    '/': InfixLexTypes.DIVIDE
}

def push_operator(obj : AbstractLexer, next_char : str):
    obj.tokens.append( (op_codes[next_char], next_char) )

def push_number(obj : AbstractLexer, next_char : str):
    obj.tokens.append( (InfixLexTypes.NUMBER, obj.token) )

number_tuple = ( push_number, push_operator, AbstractLexer.reset_token )
number_eof = (push_number, AbstractLexer.reset_token )

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
                (r'\s', 'neutral', ()),
                (r'\(','neutral', push_operator),
                (r'[0-9]','number', AbstractLexer.accumulate),
                (r'\.','number-dot', AbstractLexer.accumulate),
                (r'-','minus', push_operator)
            ],
            "number": [
                (None, 'neutral', number_eof),
                (r'\s', 'number', ()),
                (r'[0-9]', 'number', AbstractLexer.accumulate),
                (r'\)', 'expect-operator', number_tuple),
                (r'[+*(/]','neutral', number_tuple),
                (r'\.','number-dot', AbstractLexer.accumulate),
                (r'-','minus', number_tuple)
            ],
            'number-dot': [
                (None, 'neutral', number_eof),
                (r'\s', 'number-dot', ()),
                (r'[0-9]', 'number-dot', AbstractLexer.accumulate),
                (r'\)', 'expect-operator', number_tuple),
                (r'[+*(/]','neutral', number_tuple),
                (r'-','minus', number_tuple)
            ],
            'expect-operator': [
                (r'\s', 'expect-operator', ()),
                (r'[+*\(/]','neutral', push_operator),
                (r'-','minus', push_operator),
                (r'\)','expect-operator', push_operator)
            ],
            'minus': {
                (r'\s', 'minus', ()),
                (r'-','minus', push_operator),
                (r'\.','number-dot', AbstractLexer.accumulate),
                (r'[0-9]', 'number', AbstractLexer.accumulate)
            }
}

luthor = AbstractLexer(transitions, "neutral")
tokens = luthor.lex("10 + 10 + (5 / 5 - 10) + 10 / -10.581")
luthor.graphviz('./viz.gv')
print(tokens)