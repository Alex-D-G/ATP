import interpreter

f = open("codeExample2.txt", "r")
codeList = f.read()


tokens = interpreter.getTokens(codeList, 0, 1, [])
token_tree = interpreter.parseTokens(tokens, 0)
print(token_tree)
