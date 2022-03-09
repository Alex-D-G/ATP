import interpreter

f = open("codeExample2.txt", "r")
codeList = f.readlines()

print(interpreter.run_code(codeList, 0, []))
