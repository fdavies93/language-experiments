from infix import InfixLexer, InfixParser, compile
import subprocess

luthor = InfixLexer()
parser = InfixParser()

try:
    print("Welcome to Del's infix compiler. Please enter an expression you want to compile.")
    input_str = input()
    print("Now enter the file you want to output to.")
    path = input()

    tokens = luthor.lex(input_str)
    ast = parser.parse(tokens)
    compile(ast, path + ".ll")
    
    print("Compiling LLVM to binary program.")
    subprocess.run(["llc","-filetype=obj",f"{path}.ll", "-o", f"{path}.o"])
    subprocess.run(["clang",f"{path}.o","-no-pie",'-o',path])
    print("Compile complete!")

# llc -filetype=obj math.ll -o math.o
# clang math.o -no-pie -o math
# ./math || echo $?

except ValueError:
    print("Oops, that wasn't a valid input. Try again.")