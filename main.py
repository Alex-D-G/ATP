import interpreter

f = open("codeExample2.txt", "r")
codeList = f.read()

# Lexer
tokens = interpreter.getTokens(codeList, 0, 1, [])
print(tokens, '\n-------')

# Parser
token_tree = interpreter.parseTokens(tokens, 0)
print(token_tree, '\n-------')

# Interpreter
inter = interpreter.TreeInterpreter()
inter_result = inter.visit(token_tree)
print(inter_result)
