from typing import Callable, Pattern, Union
import re

LexTransitionFn = Callable[["AbstractLexer", str],None]
LexTransition = tuple[Pattern,str,Union[tuple[LexTransitionFn],LexTransitionFn]]
LexToken = tuple[int, str]

class AbstractLexer():
    def __init__(self, transitions : dict[str, list[LexTransition]], start_state : str):
        # self.ignore = '\n\r\t '
        self.token = ''
        self.tokens = []
        self.transitions = transitions
        self.state = start_state

    @classmethod
    def make_push_token_as(cls, output_int : int) -> Callable[["AbstractLexer", str],None]:
        # the obj passed is the lexer itself
        return lambda obj, next_char : obj.tokens.append( (output_int, obj.token) )

    @classmethod
    def accumulate(cls, obj : "AbstractLexer", next_char : str):
        obj.token += next_char

    @classmethod
    def reset_token(cls, obj : "AbstractLexer", next_char : str):
        obj.token = ""

    @classmethod
    def make_push_next_char_as(cls, output_int : int) -> Callable[["AbstractLexer", str],None]:
        return lambda obj, next_char : obj.tokens.append( (output_int, next_char) )

    def reset(self):
        self.token = ''
        self.tokens = []

    def step(self, next_char : str):
        # if next_char in self.ignore:
        #     return
        # print(next_char)

        matches = 0
        state = self.state
        for expr in self.transitions.get(state):
            if expr[0] != None and re.match(expr[0], next_char) != None:
                matches += 1
                
                if matches > 1:
                    raise ValueError(f"Overlapping symbol definitions in {state}")
                
                self.state = expr[1]

                if isinstance(expr[2], tuple):
                    for fn in expr[2]:
                        fn(self,next_char)
                else:
                    expr[2](self,next_char)

        if matches == 0:
            raise ValueError(f"No valid matches for next character in state {self.state}.")
    
    def graphviz(self, outPath : str):
        lines = [
            'digraph fsm {',
            'fontname="Roboto,Arial,sans-serif"',
            'node [fontname="Roboto,Arial,sans-serif"]',
            'rankdir=LR;',
            'node [shape=circle];'
        ]
        for state in self.transitions:
            for transition in self.transitions[state]:
                lines.append(f'{state.replace("-","_")} -> {transition[1].replace("-","_")} ["label" = "{str(transition[0])}"];')
        lines.append('}')

        with open(outPath, "w") as f:
            for ln in lines:
                f.write(f"{ln}\n")

    def lex(self, input : str):
        self.reset()
        for char in input:
            self.step(char)

        possible_eof = self.transitions.get(self.state)[0]
        
        if possible_eof[0] == None:
            if isinstance(possible_eof[2], tuple):
                for fn in possible_eof[2]:
                    fn(self,"")
            else:
                possible_eof[2](self,"")
        
        return self.tokens