import sys
from lexer import Lexer
from parser import Parser
from interpreter import Interpreter

def run_js(code):
    try:
        lexer = Lexer(code)
        tokens = lexer.tokenize()
        
        parser = Parser(tokens)
        ast = parser.parse()
        
        interpreter = Interpreter()
        interpreter.interpret(ast)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        with open(sys.argv[1], 'r') as f:
            code = f.read()
        run_js(code)
    else:
        print("Usage: python main.py <filename.js>")
