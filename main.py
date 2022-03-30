import compiler

f = open("codeExample.txt", "r")
codeList = f.readlines()

# Run the Compiler
value, varList, funcList, checkpointList, resultStr, additionalStr = compiler.run_code(codeList, 0, [], [], [], 0, "", False, False)

