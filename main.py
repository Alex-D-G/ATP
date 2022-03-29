import compiler

f = open("codeExample.txt", "r")
codeList = f.readlines()

# This external code from the interpreter runs the required functions
value, varList, funcList, checkpointList, resultStr, additionalStr = compiler.run_code(codeList, 0, [], [], [], 0, "", False, False)

