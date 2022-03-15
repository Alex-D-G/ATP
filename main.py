import interpreter

f = open("codeExample2.txt", "r")
codeList = f.readlines()


result = interpreter.run_code(codeList, 0, [], [], [], 0)
print("--------")
print('result:', result)
