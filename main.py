import interpreter

f = open("codeExample.txt", "r")
codeList = f.readlines()

# This external code from the interpreter runs the required functions

result0 = interpreter.runFunc(codeList, 'even', [6])
print('Is 6 even?:', result0)
result1 = interpreter.runFunc(codeList, 'odd', [6])
print('Is 6 odd?:', result1)
result2 = interpreter.runFunc(codeList, 'sommig', [6, 10])
print('sommig result:', result2)
