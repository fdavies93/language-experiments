# Infix Parser Reference

This is a parser & lexer for infix algebra which I wrote as a reference for future projects. Also included is a (flawed) BNF grammar for infix algebra.

It can handle all standard one-character operations (`+`, `-`, `/`, `*`) as well as brackets and expressions using a unary `-`. Support for `^` is broken and unlikely to be fixed.

One peculiarity of this parser is that it interprets all `-` signs as unary `-`. Expressions like `10 - 10` are lexed to `10 + -10`. One consequence of this is that addition and subtraction have equal precedence: i.e. `10 + 10 - 10 + 10` will evaluate to `20`, not `30`. Another is that subtraction operations have precedence issues: `10 - 10 * 10` will output as `110` rather than `-90`.

This is an operator-precedence parser, which is a relative of an LR parser with fewer capabilities. They are both types of shift-reduce parser.

While it does use recursion to simplify the code (bad) it could be implemented as a simple stack and a previous attempt using the same strategy did so.