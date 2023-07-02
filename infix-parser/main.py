from infix import InfixLexer, InfixParser, evaluate

luthor = InfixLexer()
parser = InfixParser()

print("Welcome to Super Simple Calculator!")
while (True):
    input_str = input("> ")
    try:
        tokens = luthor.lex(input_str)
        ast = parser.parse(tokens)
        print(evaluate(ast))
    except ValueError:
        print("Oops, that wasn't a valid input. Try again.")