# Del's Language Experiments

This repository is a set of experiments in language lexing, parsing, and compiler design.

## Projects

`abstract-lexer` is an abstract state machine for lexing, which can take a set of rules (not a grammar) and output tokens based on those rules.

`infix-parser` is an operator-precedence parser for infix expressions - the same type of parser that a calculator might use. It runs an interpreter and can also compile to LLVM assembly.

`infix-plus` implements a functional toy language based on math notation and using a recursive descent parser implemented based on a PEG grammar, combined with tokens output from the abstract lexer project.