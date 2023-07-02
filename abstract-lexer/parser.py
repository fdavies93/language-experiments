from typing import Callable, Union, Iterable
from lexer import LexToken
import re

# ParseTransitionFn
# (parser, next_token)
ParseTransitionFn = Callable[["AbstractParser",str],None]
# ParseTransition:
# (token_id, next_state, actions)
ParseTransition = tuple[tuple[int],str,Union[tuple[ParseTransitionFn], ParseTransitionFn]]

class AbstractParser:
    def __init__(self, transitions : dict[str, list[ParseTransition]], start_state : str):
        self.stack = []
        self.tape = []
        self.transitions = transitions
        self.current_state = start_state

    def parse(self, tokens : Iterable[LexToken]):
        self.tape = tokens
        while len(self.tape) > 0:
            self.transitions.get(self.current_state)