from tokens import *
from typing import Union, Callable, Tuple, List, TypeVar


# =============== LEXER =====================


# This function checks if a given char is a number
def checkNumber(char: str) -> bool:
    return char.isdigit()


# This function checks if a given char is alphabetical
def checkWord(char: str) -> bool:
    return char.isalpha()


# Higher order function used for checking chars
def getExtension(func: Callable[[str], bool], codeText: str, index: int) -> str:
    if index != len(codeText) and func(codeText[index]):
        # Loop recursively and add the result to codeText
        return codeText[index] + getExtension(func, codeText, index + 1)
    return ''


# Lexer function, this function loops through a given string in order to collect all tokens
def getTokens(codeText: str, index: int, result: List[Token]) -> List[Token]:
    # If the end of the line in reached return result
    if index == len(codeText):
        return result
    else:
        tmp_token = codeText[index]
        if tmp_token.isdigit():
            # Collects all connected numbers
            number = tmp_token + getExtension(checkNumber, codeText, index + 1)
            return getTokens(codeText, index + len(number), result + [Token(NUMBER, number)])

        elif tmp_token.isalpha():
            # Collects all connected alphabetical chars
            word = tmp_token + getExtension(checkWord, codeText, index + 1)
            # Check if the word found is a Keyword
            if word in KEYWORDS:
                return getTokens(codeText, index + len(word), result + [Token(KEYWORD, word)])
            return getTokens(codeText, index + len(word), result + [Token(NAME, word)])

        # skip the char of its empty or and endline
        elif tmp_token == ' ' or tmp_token == '\n':
            if tmp_token == '\n':
                return getTokens(codeText, index + 1, result)
            return getTokens(codeText, index + 1, result)

        elif tmp_token == '>':
            # check if the next tokens combine to form a '>>>'
            if (tmp_token + codeText[index + 1] + codeText[index + 2]) == '>>>':
                return getTokens(codeText, index + 3, result + [Token(GO_TO, '>>>')])
            # check if the next tokens combine to form a '>='
            elif (tmp_token + codeText[index + 1]) == '>=':
                return getTokens(codeText, index + 2, result + [Token(GREATER_OR_EQUAL_TO, '>=')])
            return getTokens(codeText, index + 1, result + [Token(GREATER_THAN, tmp_token)])

        elif tmp_token == '<':
            # check if the next tokens combine to form a '<='
            if (tmp_token + codeText[index + 1]) == '<=':
                return getTokens(codeText, index + 2, result + [Token(LESSER_OR_EQUAL_TO, '<=')])
            return getTokens(codeText, index + 1, result + [Token(LESSER_THAN, tmp_token)])

        elif tmp_token == '(':
            return getTokens(codeText, index + 1, result + [Token(OPEN_BRACKET, tmp_token)])

        elif tmp_token == ')':
            return getTokens(codeText, index + 1, result + [Token(CLOSE_BRACKET, tmp_token)])

        elif tmp_token == '{':
            return getTokens(codeText, index + 1, result + [Token(OPEN_C_BRACKET, tmp_token)])

        elif tmp_token == '}':
            return getTokens(codeText, index + 1, result + [Token(CLOSE_C_BRACKET, tmp_token)])

        elif tmp_token == '=':
            # check if the next tokens combine to form a '=='
            if (tmp_token + codeText[index + 1]) == '==':
                return getTokens(codeText, index + 2, result + [Token(IS_EQUAL_TO, '==')])
            return getTokens(codeText, index + 1, result + [Token(EQUAL, tmp_token)])

        elif tmp_token == '-':
            # check if '-' is the first token in the list, indicating that it's part of a negative number
            if len(result) == 0:
                number = tmp_token + getExtension(checkNumber, codeText, index + 1)
                return getTokens(codeText, index + len(number), result + [Token(NUMBER, number)])
            # check if '-' is behind an operator, indicating that it's part of a negative number
            elif result[-1].type in [MINUS, PLUS, MULTIPLY, OPEN_BRACKET]:
                number = tmp_token + getExtension(checkNumber, codeText, index + 1)
                return getTokens(codeText, index + len(number), result + [Token(NUMBER, number)])

            return getTokens(codeText, index + 1, result + [Token(MINUS, tmp_token)])

        elif tmp_token == '+':
            return getTokens(codeText, index + 1, result + [Token(PLUS, tmp_token)])

        elif tmp_token == '*':
            return getTokens(codeText, index + 1, result + [Token(MULTIPLY, tmp_token)])

        elif tmp_token == '?':
            return getTokens(codeText, index + 1, result + [Token(IF, tmp_token)])

        elif tmp_token == ',':
            return getTokens(codeText, index + 1, result + [Token(COMMA, tmp_token)])

        # If it's unknown token, skip it
        return getTokens(codeText, index + 1, result)


# ========== List manipulation ===============

# Class used for saving variables
class Variable(NamedTuple):
    name: str
    location: str


A = TypeVar('A')  # used mostly for varList
B = TypeVar('B')  # used mostly for checkpointList


# This functions collects all names from elements in a given list
def getListNames(varList: List[A], index: int, results: List[str]) -> List[str]:
    if index == len(varList):
        return results
    return getListNames(varList, index + 1, results + [varList[index].name])


# Function that used to decorate getListNames in order for it to check if a given name is in the list
def getListNamesDecorator(func: Callable[[List[A], int, List[str]], List[str]]):
    index = 0
    results = []

    def inner(varList: List[A], name: str) -> bool:
        nameList = func(varList, index, results)
        return name in nameList

    return inner


# This function checks if a given name is in a given list
checkIfNameInList = getListNamesDecorator(getListNames)


# This functions removes a given var name from a varList
def removeTargetFromList(varList: List[A], varName: str, index: int, newVarList: List[A]) -> List[A]:
    if index == len(varList):
        return newVarList
    # Check if varName is equal to the current name, if so skip this var
    if varList[index].name == varName:
        return removeTargetFromList(varList, varName, index + 1, newVarList)
    return removeTargetFromList(varList, varName, index + 1, newVarList + [varList[index]])


# This function applies a given function to a list
def applyFuncToList(func: Callable[[List[A], str, int, List[A]], List[A]],
                    targetList: List[A], varList: List[A], index: int) -> List[A]:
    if index == len(targetList):
        return varList

    # apply function to list and index
    newList = func(varList, targetList[index], 0, [])
    return applyFuncToList(func, targetList, newList, index + 1)


# This functions converts a list of given tokens to vars, used for collecting function vars
def getVarsFromTokens(tokens: List[Token], index: int, varList: List[Variable]) -> List[Union[List[Variable], int]]:
    if tokens[index].type == CLOSE_BRACKET:
        return [varList, index]
    # if token is a number or a name (a variable) add it to the varlist
    elif tokens[index].type == NUMBER or tokens[index].type == NAME:
        new_vars = varList + [Variable(tokens[index].value, "r"+str(len(varList)))]
        return getVarsFromTokens(tokens, index + 1, new_vars)
    elif tokens[index].type == COMMA:
        return getVarsFromTokens(tokens, index + 1, varList)


# This functions converts a list of given tokens to nodes, used for collecting function vars
def getNodesFromTokens(tokens: List[Token], index: int, varList: List[A], funcList: List['FuncContext'],
                       result: List['Node']) -> Tuple[List['Node'], int]:
    # Check if the end of function variables is reached
    if tokens[index - 1].type == CLOSE_BRACKET:
        return result, index

    # Gather a variable node
    new_node, new_index = expression(tokens, index, varList, funcList)
    return getNodesFromTokens(tokens, new_index + 1, varList, funcList, result + [new_node])


# This functions looks for the ending line of an if or function
def findEndOfContext(codeList: List[str], index: int, lineNumber: int, amountOpen: int, amountClosed: int) -> int:
    # Check if there is an equal amount of opens as there is closes, if so the end is reached
    if amountOpen == amountClosed:
        return lineNumber
    # If current char is an endline go the next line
    elif codeList[lineNumber][index] == '\n':
        return findEndOfContext(codeList, 0, lineNumber + 1, amountOpen, amountClosed)
    elif codeList[lineNumber][index] == '}':
        # Loop further through the chars and add 1 to amount closed,
        # also add 1 to lineNumber since '}' is always at the end of a line
        return findEndOfContext(codeList, 0, lineNumber + 1, amountOpen, amountClosed + 1)
    elif codeList[lineNumber][index] == '{':
        # Loop further through the chars and add 1 to amount closed,
        # also add 1 to lineNumber since '{' is always at the end of a line
        return findEndOfContext(codeList, 0, lineNumber + 1, amountOpen + 1, amountClosed)
    return findEndOfContext(codeList, index + 1, lineNumber, amountOpen, amountClosed)


# =============== PARSER nodes =====================


# Node for a function call
class FuncCallNode(NamedTuple):
    name: str
    varList: List[A]


# Node for a function declaration
class FuncCreateNode(NamedTuple):
    name: str
    varList: List[A]


# Node for a basic token
class TokenNode(NamedTuple):
    tok: Token


# Node for a variable
class VarNode(NamedTuple):
    name: Token
    value: 'Node'


# Node for an if statement
class IfNode(NamedTuple):
    value: 'Node'


# Node for a return statement
class ReturnNode(NamedTuple):
    value: 'Node'


# Node for an operator
class OpNode(NamedTuple):
    left_node: 'Node'
    operator: Token
    right_node: 'Node'


# Node for a checkpoint statement
class CheckpointNode(NamedTuple):
    name: str


# Node for a GoTo statement
class GoToNode(NamedTuple):
    name: str


# This Union makes it possible to return a variety of nodes from one function
Node = Union[TokenNode, OpNode, VarNode, FuncCreateNode, FuncCallNode, ReturnNode, IfNode, CheckpointNode, GoToNode]


# =============== PARSER =====================

# This function handles the creation of the different nodes
def NodeCreation(tokens: List[Token], index: int, varList: List[A], funcList: List['FuncContext']) -> Tuple[Node, int]:
    # Check for different node syntax

    if tokens[index].type == IF:
        # Check if syntax is correct
        if tokens[index + 1].type == OPEN_BRACKET:
            if tokens[-2].type == CLOSE_BRACKET and tokens[-1].type == OPEN_C_BRACKET:
                # Get the comparison operator node
                New_node, new_index = comparison(tokens, index + 2, varList, funcList)
                return IfNode(New_node), new_index + 1

    elif tokens[index].type == NAME:

        # Check if the name is a variable
        if checkIfNameInList(varList, tokens[index].value):
            if index + 1 != len(tokens):
                # Check if its assigning a new value to the variable, if not create a var call
                if tokens[index + 1].type == EQUAL:
                    New_node, new_index = expression(tokens, index + 2, varList, funcList)

                    return VarNode(tokens[index], New_node), new_index
            return TokenNode(tokens[index]), index + 1  # Var call

        # Check if  the name is a function
        if tokens[index + 1].type == OPEN_BRACKET:
            # Gather all nodes between the brackets
            Node_list, new_index = getNodesFromTokens(tokens, index + 2, varList, funcList, [])
            return FuncCallNode(tokens[index].value, Node_list), new_index

    elif tokens[index].type == KEYWORD and tokens[index].value == 'var':
        # Check if syntax is correct
        if tokens[index + 1].type == NAME and tokens[index + 2].type == EQUAL:
            variable_name = tokens[index + 1]
            # Gather the node contain the new variable's value
            New_node, new_index = expression(tokens, index + 3, varList, funcList)

            return VarNode(variable_name, New_node), new_index

    elif tokens[index].type == KEYWORD and tokens[index].value == 'func':  # Function declaration
        # Check if syntax is correct
        if tokens[index + 1].type == NAME:
            if tokens[index + 2].type == OPEN_BRACKET:
                if tokens[-2].type == CLOSE_BRACKET and tokens[-1].type == OPEN_C_BRACKET:
                    # Collect the function's variables
                    new_vars = getVarsFromTokens(tokens, index + 3, [])[0]
                    return FuncCreateNode(tokens[index + 1].value, new_vars), len(tokens)

    elif tokens[index].type == KEYWORD and tokens[index].value == 'return':
        # Get the node after the return
        New_node, new_index = expression(tokens, index + 1, varList, funcList)
        return ReturnNode(New_node), new_index

    elif tokens[index].type == KEYWORD and tokens[index].value == 'checkpoint':
        # Check if syntax is correct
        if tokens[index + 1].type == NAME:
            return CheckpointNode(tokens[index + 1].value), index + 2

    elif tokens[index].type == GO_TO:
        # Check if syntax is correct
        if tokens[index + 1].type == NAME:
            return GoToNode(tokens[index + 1].value), index + 2

    elif tokens[index].type == NUMBER:
        return TokenNode(tokens[index]), index + 1

    elif tokens[index].type == OPEN_BRACKET:
        # Get the node beside bracket
        New_node, new_index = expression(tokens, index + 1, varList, funcList)
        return New_node, new_index + 1
    raise Exception(tokens[index], " is not known")


# This function handles opNodes involving multiplication
def term(tokens: List[Token], index: int, varList: List[A], funcList: List['FuncContext']) -> Tuple[Node, int]:
    return operation(NodeCreation, MULTIPLY, tokens, index, varList, funcList)


# This function handles opNodes involving plus or minus
def expression(tokens: List[Token], index: int, varList: List[A], funcList: List['FuncContext']) -> Tuple[Node, int]:
    return operation(term, [PLUS, MINUS], tokens, index, varList, funcList)


# This function handles opNodes comparing between two nodes
def comparison(tokens: List[Token], index: int, varList: List[A], funcList: List['FuncContext']) -> Tuple[Node, int]:
    return operation(NodeCreation, [LESSER_THAN, GREATER_THAN, GREATER_OR_EQUAL_TO, LESSER_OR_EQUAL_TO, IS_EQUAL_TO],
                     tokens, index, varList, funcList)


# This function looks for operator nodes using the provided operators
def operationSearch(func: Callable[[List[Token], int, List[A], List['FuncContext']], Tuple[Node, int]],
                    operators: List[str], tokens: List[Token], index: int, left_node: Node,
                    varList: List[Token], funcList: List['FuncContext']) -> Tuple[Node, int]:
    # If the end of the tokens is reached return the left node
    if len(tokens) <= index:
        return left_node, index
    # If the current token is not in the provided operators return the left node
    elif tokens[index].type not in operators:
        return left_node, index

    # Grabs the current operator
    operator_token = tokens[index]
    # Collects the right_node
    right_node, new_index = func(tokens, index + 1, varList, funcList)

    return operationSearch(func, operators, tokens, new_index,
                           OpNode(left_node, operator_token, right_node), varList, funcList)


# This function starts operationSearch
def operation(func: Callable[[List[Token], int, List[A], List['FuncContext']], Tuple[Node, int]], operators: List[str],
              tokens: List[Token], index: int, varList: List[A], funcList: List['FuncContext']) -> Tuple[Node, int]:
    # Create a left node used by operationSearch
    left, new_index = func(tokens, index, varList, funcList)
    return operationSearch(func, operators, tokens, new_index, left, varList, funcList)


# This function starts the parsing process
def parseTokens(tokens: List[Token], index: int, varList: List[A], funcList: List['FuncContext']) -> Node:
    result, unused_index = expression(tokens, index, varList, funcList)
    return result


# ========= Compiler return types ==============


# This class is used for returning new functions
class FuncReturn(NamedTuple):
    name: Token
    varList: List[str]


# This class is used for returning variables
class VarReturn(NamedTuple):
    name: str
    value: int


# This class is used for returning numbers
class IntReturn(NamedTuple):
    value: int


# This class is used for returning return statements
class ReturnReturn(NamedTuple):
    value: int


# This class is used for returning if statement results
class IfReturn(NamedTuple):
    value: str


# This class is used for returning new checkpoints
class CheckpointReturn(NamedTuple):
    value: Token


# This Union allows functions to return multiple types of return
ReturnType = Union[IntReturn, VarReturn, FuncReturn, ReturnReturn, IfReturn, CheckpointReturn]


# =============== COMPILER =====================

# Creates a string that contains the loading of function variables
def loadFuncVars(funcVars: List[Node], varList: List[A], index: int, resultStr: str) -> str:
    if len(funcVars) == index:
        return resultStr

    elif funcVars[index].tok.type == NUMBER:
        newVarStr = "movs   r" + str(index) + ", #" + funcVars[index].tok.value + "\n"
        return loadFuncVars(funcVars, varList, index+1, resultStr + newVarStr)

    elif funcVars[index].tok.type == NAME:
        if checkIfNameInList(varList, funcVars[index].tok.value):
            varNames = getListNames(varList, 0, [])
            storeLocation = varList[varNames.index(funcVars[index].tok.value)].location
            if storeLocation == "0":
                newVarStr = "ldr   r" + str(index) + ", [sp]\n"
                return loadFuncVars(funcVars, varList, index + 1, resultStr + newVarStr)

            newVarStr = "ldr   r" + str(index) + ", [sp, #" + storeLocation + "]\n"
            return loadFuncVars(funcVars, varList, index+1, resultStr + newVarStr)


# This class contains all the compiler visit functions
class Compiler:
    # This function send the node to the correct visit function
    def visit(self, node: Node, varList: List[A], funcList: List['FuncContext'],
              checkpointList: List[B]) -> ReturnType:

        # Create the method function's name
        method_name = f'visit_{type(node).__name__}'
        # Get the function
        method = getattr(self, method_name)
        return method(node, varList, funcList, checkpointList)

    # This function returns the basis for a newly created function
    @staticmethod
    def visit_FuncCreateNode(funcNode: Node, varList: List[A], funcList: List['FuncContext'],
                             checkpointList: List[B]) -> Tuple[ReturnType, str]:
        name = str(funcNode.name)+":"
        result = name
        return FuncReturn(funcNode.name, funcNode.varList), result

    # This function returns a function call str
    def visit_FuncCallNode(self, funcNode: Node, varList: List[A], funcList: List['FuncContext'],
                           checkpointList: List[B]) -> Tuple[ReturnType, str]:
        loadedVars = loadFuncVars(funcNode.varList, varList, 0, "")
        branchFunc = "bl    " + funcNode.name
        return IntReturn(0), loadedVars + branchFunc

    # This function returns a newly created checkpoint
    @staticmethod
    def visit_CheckpointNode(checkpointNode: Node, varList: List[A], funcList: List['FuncContext'],
                             checkpointList: List[B]) -> Tuple[ReturnType, str]:

        checkpointStr = ".LCB" + str(len(funcList)) + "_" + str(len(checkpointList)+1)
        return CheckpointReturn(checkpointNode.name), checkpointStr

    # This function returns a go to string
    @staticmethod
    def visit_GoToNode(goToNode: Node, varList: List[A], funcList: List['FuncContext'],
                       checkpointList: List[B]) -> Tuple[ReturnType, str]:

        if checkIfNameInList(checkpointList, goToNode.name):
            checkpointNames = getListNames(checkpointList, 0, [])
            storeLocation = checkpointList[checkpointNames.index(goToNode.name)].address
            GoToStr = "b     " + storeLocation
            return IntReturn(0), GoToStr

    # This function returns the branch str
    def visit_IfNode(self, ifNode: Node, varList: List[A], funcList: List['FuncContext'],
                     checkpointList: List[B]) -> Tuple[ReturnType, str]:

        leftReturn, leftStr = self.visit_TokenNode(ifNode.value.left_node, varList, funcList, checkpointList, 0)    # Get the left token
        rightReturn, rightStr = self.visit_TokenNode(ifNode.value.right_node, varList, funcList, checkpointList, 1)  # Get the right token
        compareStr = "cmp   r0, r1\n"

        if ifNode.value.operator.type == LESSER_THAN:                           # <
            return IfReturn(LESSER_THAN), leftStr+rightStr+compareStr
        elif ifNode.value.operator.type == GREATER_THAN:                        # >
            return IfReturn(GREATER_THAN), leftStr+rightStr+compareStr
        elif ifNode.value.operator.type == IS_EQUAL_TO:                         # ==
            return IfReturn(IS_EQUAL_TO), leftStr+rightStr+compareStr
        elif ifNode.value.operator.type == GREATER_OR_EQUAL_TO:                 # >=
            return IfReturn(GREATER_OR_EQUAL_TO), leftStr+rightStr+compareStr
        elif ifNode.value.operator.type == LESSER_OR_EQUAL_TO:                  # <=
            return IfReturn(LESSER_OR_EQUAL_TO), leftStr+rightStr+compareStr

    # This function returns the result of the node provided to the return node
    def visit_ReturnNode(self, returnNode: Node, varList: List[A], funcList: List['FuncContext'],
                         checkpointList: List[B]) -> Tuple[ReturnType, str]:

        if type(returnNode.value) == TokenNode:
            if returnNode.value.tok.type == NAME:  # if you return a variable
                if checkIfNameInList(varList, returnNode.value.tok.value):
                    varNames = getListNames(varList, 0, [])
                    storeLocation = varList[varNames.index(returnNode.value.tok.value)].location
                    if storeLocation == '0':
                        return ReturnReturn(0), "ldr   r0, [sp]"
                    return ReturnReturn(0), "ldr   r0, [sp, #"+storeLocation+"]"

            elif returnNode.value.tok.type == NUMBER:  # if you return an int
                return ReturnReturn(0), "movs  r0, #" + str(returnNode.value.tok.value)

        return ReturnReturn(0), "RETURN"

    # This function creates a new variable and returns it
    def visit_VarNode(self, varNode: Node, varList: List[A], funcList: List['FuncContext'],
                      checkpointList: List[B]) -> Tuple[ReturnType, str]:

        if type(varNode.value) == TokenNode:  # If the variable is assigned with a token
            if varNode.value.tok.type == NUMBER:
                movValue = "movs  r0, #" + varNode.value.tok.value
                return VarReturn(varNode.name.value, 10), movValue
            if varNode.value.tok.type == NAME:
                return VarReturn(varNode.name.value, 10), "Var assign with Var"

        if type(varNode.value) == OpNode:  # If the variable is assigned with a operation
            leftReturn, leftStr = self.visit_TokenNode(varNode.value.left_node, varList, funcList, checkpointList, 0)
            rightReturn, rightStr = self.visit_TokenNode(varNode.value.right_node, varList, funcList, checkpointList, 1)

            if varNode.value.operator.type == PLUS:
                opStr = "add   r0, r0, r1"
                returnStr = leftStr + rightStr + opStr
                return VarReturn(varNode.name.value, 10), returnStr
            elif varNode.value.operator.type == MINUS:
                opStr = "sub   r0, r0, r1"
                returnStr = leftStr + rightStr + opStr
                return VarReturn(varNode.name.value, 10), returnStr
            elif varNode.value.operator.type == MULTIPLY:
                opStr = "mul   r0, r0, r1"
                returnStr = leftStr + rightStr + opStr
                return VarReturn(varNode.name.value, 10), returnStr

        if type(varNode.value) == FuncCallNode:  # If the variable is assigned with a func call
            leftReturn, funcStr = self.visit_FuncCallNode(varNode.value, varList, funcList, checkpointList)
            return VarReturn(varNode.name.value, 10), funcStr

        return VarReturn(varNode.name.value, 10), "Var"

    # This function returns the value of a provided Token
    @staticmethod
    def visit_TokenNode(tokenNode: Node, varList: List[A], funcList: List['FuncContext'],
                        checkpointList: List[B], target_reg: int) -> Tuple[ReturnType, str]:

        if tokenNode.tok.type == NUMBER:
            assignStr = "movs  r" + str(target_reg) + ", #" + tokenNode.tok.value + "\n"
            return IntReturn(0), assignStr

        if tokenNode.tok.type == NAME:
            varNames = getListNames(varList, 0, [])
            # Check if the called function exists
            if tokenNode.tok.value in varNames:
                # Get the called function from the function list
                targetVar = varList[varNames.index(tokenNode.tok.value)]
                if targetVar.location == '0':
                    assignStr = "ldr   r" + str(target_reg) + ", [sp]\n"
                    return IntReturn(0), assignStr
                assignStr = "ldr   r" + str(target_reg) + ", [sp, #" + targetVar.location + "]\n"
                return IntReturn(0), assignStr

        return IntReturn(0), "Token"


# =============== CONTROLLER =====================

# This Class holds all the information needed for a function
class FuncContext(NamedTuple):
    name: Token
    varList: List[A]
    start: int
    end: int


# This Class holds all the information needed for a checkpoint
class Checkpoint(NamedTuple):
    name: Token
    address: str


# This function returns the string at the start of the .asm
def createIntroText(funcList: List[FuncContext], index: int, result: str) -> str:
    if index == len(funcList):
        return ".cpu cortex-m0\n.text\n.align 2\n\n"+result+"\n\n"
    new_str = ".global "+str(funcList[index].name)+"\n"
    return createIntroText(funcList, index+1, result + new_str)


# This function add tabs to all lines given
def addTabs(inputStr: str, index: int, outputStr: str) -> str:
    if index == len(inputStr):
        return outputStr
    elif index == 0:
        return addTabs(inputStr, index + 1, outputStr + "   " + inputStr[index])
    elif inputStr[index] == "\n":
        return addTabs(inputStr, index+1, outputStr + inputStr[index] + "   ")
    return addTabs(inputStr, index + 1, outputStr + inputStr[index])


def removeTabs(inputStr: str, index: int, outputStr: str) -> str:
    if index == len(inputStr) or inputStr[index] != " ":
        return outputStr + inputStr[index:]
    if inputStr[index] == " ":
        return removeTabs(inputStr, index+1, outputStr)
    return removeTabs(inputStr, index+1, outputStr+inputStr[index])


# This function creates a str containing the asm instructions for storing the provided var list
def storeVarlist(varList: List[A], index: int, result: str, newVarlist: List[A]) -> Tuple[str, List[A]]:
    if index == len(varList):
        return result, newVarlist
    if index == 0:
        storeVar = "   str   " + varList[index].location + ", [sp]\n"
        return storeVarlist(varList, index+1, result + storeVar, newVarlist + [Variable(varList[index].name, "0")])
    storeVar = "   str   " + varList[index].location + ", [sp, #" + str(index*4) + "]\n"
    return storeVarlist(varList, index + 1, result + storeVar, newVarlist +
                        [Variable(varList[index].name, str(index*4))])


# Check if there is a return token in the given token list
def checkForReturnToken(tokens: List[Token], index: int) -> bool:
    if index == len(tokens):
        return False
    elif tokens[index].value == "return":
        return True
    return checkForReturnToken(tokens, index+1)


# Check if there are multiple return tokens in a code segment
def lookForDoubleReturn(codeList: List[str], index: int, end: int, returnCount: int) -> bool:
    if returnCount == 2:
        return True
    elif index == end:
        return False
    tokens = getTokens(codeList[index], 0, [])
    if checkForReturnToken(tokens, 0):
        return lookForDoubleReturn(codeList, index+1, end, returnCount+1)
    return lookForDoubleReturn(codeList, index+1, end, returnCount)


# Check if there is a function call within a token list
def checkForFunctionToken(tokens: List[Token], index: int, funcNames: List[str]) -> bool:
    if index == len(tokens):
        return False
    if index + 1 < len(tokens):
        if tokens[index].type == NAME and tokens[index + 1].type == OPEN_BRACKET:
            return True
    return checkForFunctionToken(tokens, index + 1, funcNames)


# Look through a section of code for something
def lookThroughCode(func: Callable[[List[Token], int, A], bool], codeList: List[str], index: int,
                    end: int, parameter: A) -> bool:

    if index == end:
        return False
    tokens = getTokens(codeList[index], 0, [])
    if func(tokens, 0, parameter):
        return True
    return lookThroughCode(func, codeList, index+1, end, parameter)


# Create the end of an asm function
def createEndStr(funcCallInFunc: bool, varList: List[A]) -> str:
    if funcCallInFunc:
        return "add   sp, #" + str(len(varList) * 4) + "\npop   {r7, pc}\n\n"
    return "add   sp, #" + str(len(varList) * 4) + "\nbx    lr\n\n"


# Create all needed branches
def createBranches(varList: List[A], funcList: List[FuncContext], branchStr1: str, branchStr2: str,
                   funcCallInFunc: bool, multipleReturns: bool) -> str:

    endStr1 = "add   sp, #" + str(len(varList) * 4) + "\nbx    lr\n\n"
    if multipleReturns:  # If multiple returns are present, create a 3rd branch for returning
        ifBranch = ".LBB" + str(len(funcList)) + "_1:\n" + addTabs(branchStr1.replace(endStr1, "", 1), 0, "") + \
                   "b     .LBB" + str(len(funcList)) + "_3\n"
        endStr2 = createEndStr(funcCallInFunc, varList)
        endBranch = ".LBB" + str(len(funcList)) + "_2:\n" + addTabs(branchStr2.replace(endStr2, "", 1) + "b     .LBB" +
                                                                    str(len(funcList)) + "_3\n", 0, "" )
        returnBranch = ".LBB" + str(len(funcList)) + "_3:\n" + addTabs(endStr2, 0, "")

        return ifBranch + "\n" + endBranch + "\n" + returnBranch

    ifBranch = ".LBB" + str(len(funcList)) + "_1:\n" + addTabs(branchStr1.replace(endStr1, "", 1), 0, "") + \
               "b     .LBB" + str(len(funcList)) + "_2\n"
    endBranch = ".LBB" + str(len(funcList)) + "_2:\n" + addTabs(branchStr2, 0, "")

    return ifBranch + "\n" + endBranch


# This function is the main control function, it goes line for line through the code until an end is reached
def run_code(codeList: List[str], lineNumber: int, varList: List[A], funcList: List[FuncContext],
             checkpointList: List[B], endOfContext: int, outputStr: str, funcCallInFunc: bool, multipleReturns: bool) \
             -> Tuple[ReturnType, List[A], List[FuncContext], List[B], str, str]:

    # Check if the end of the file is reached
    if len(codeList) == lineNumber:
        introText = createIntroText(funcList, 0, "")
        f = open("demofile.asm", "w")
        f.write(introText+outputStr)
        f.close()
        # Return 0, meaning there was no return found
        return IntReturn(0), varList, funcList, checkpointList, outputStr, ""

    # Check if the end of a context is reached
    elif endOfContext and endOfContext - 1 == lineNumber:
        return IntReturn(0), varList, funcList, checkpointList, outputStr + createEndStr(funcCallInFunc, varList), ""

    # Check if the current line is empty
    elif codeList[lineNumber][0] == '\n' or codeList[lineNumber][0] == "}":
        return run_code(codeList, lineNumber + 1, varList, funcList, checkpointList, endOfContext, outputStr,
                        funcCallInFunc, multipleReturns)

    # Add a comment to the .asm file explaining what line the code translates to
    CommentedOutputStr = outputStr + "// " + removeTabs(codeList[lineNumber], 0, "")

    # Call the Lexer
    tokens = getTokens(codeList[lineNumber], 0, [])
    if tokens[0].type == CLOSE_C_BRACKET:
        return run_code(codeList, lineNumber + 1, varList, funcList, checkpointList, endOfContext, CommentedOutputStr,
                        funcCallInFunc, multipleReturns)

    # Call the Parser
    token_tree = parseTokens(tokens, 0, varList, funcList)

    # Create the Compiler class
    compiler = Compiler()
    # Call the Compiler
    compile_result, str_result = compiler.visit(token_tree, varList, funcList, checkpointList)

    if type(compile_result) == FuncReturn:  # If the compiler returns a function, compile the rest of that function
        contextEnd = findEndOfContext(codeList, 0, lineNumber + 1, 1, 0)
        new_func = FuncContext(compile_result.name, compile_result.varList, lineNumber, contextEnd)
        funcVarList = applyFuncToList(removeTargetFromList, varList, new_func.varList, 0)
        storedVarStr, newFuncVars = storeVarlist(funcVarList, 0, "", [])

        multipleReturnsPresent = lookForDoubleReturn(codeList, lineNumber + 1, contextEnd - 1, 0)
        functionCallPresent = lookThroughCode(checkForFunctionToken, codeList, lineNumber + 1, contextEnd - 1,
                                              getListNames(funcList, 0, []))
        # Compile the contents of the function
        return_value, newVars, newFuncList, newCheckpointList, returnedStr, additionalStr = run_code(
            codeList, new_func.start + 1, newFuncVars, funcList, checkpointList, new_func.end,
            "", functionCallPresent, multipleReturnsPresent)

        if functionCallPresent:  # If a function call is present within the function, push r7
            makeSpaceStr = "   push  {r7, lr}\n" \
                           "   add   r7, sp, #0\n" \
                           "   sub   sp, #" + str(len(newVars) * 4) + "\n"
            if additionalStr == "":  # If there is no if statement
                newOutputStr = CommentedOutputStr + str_result + "\n" + makeSpaceStr + storedVarStr + \
                               addTabs(returnedStr, 0, "") + "\n\n"
                return run_code(codeList, contextEnd, newFuncVars, funcList + [new_func], checkpointList, endOfContext,
                                newOutputStr, funcCallInFunc, multipleReturns)

            newOutputStr = CommentedOutputStr + str_result + "\n" + makeSpaceStr + storedVarStr + \
                           addTabs(returnedStr, 0, "") + "\n\n" + additionalStr + "\n"
            return run_code(codeList, contextEnd, newFuncVars, funcList + [new_func], checkpointList, endOfContext,
                            newOutputStr, funcCallInFunc, multipleReturns)

        makeSpaceStr = "   sub   sp, #" + str(len(newVars) * 4) + "\n"
        if additionalStr == "":  # If there is no if statement
            newOutputStr = CommentedOutputStr + str_result + "\n" + makeSpaceStr + storedVarStr + addTabs(returnedStr, 0, "")
            return run_code(codeList, contextEnd, newFuncVars, funcList + [new_func], checkpointList, endOfContext,
                            newOutputStr + "\n\n", funcCallInFunc, multipleReturns)

        newOutputStr = CommentedOutputStr + str_result + "\n" + makeSpaceStr + storedVarStr + addTabs(returnedStr, 0, "") +\
                       "\n\n" + additionalStr + "\n"
        return run_code(codeList, contextEnd, newFuncVars, funcList + [new_func], checkpointList, endOfContext,
                        newOutputStr, funcCallInFunc, multipleReturns)

    elif type(compile_result) == IfReturn:  # If the compiler returns an If, compile the contents of the If
        endOfIf = findEndOfContext(codeList, 0, lineNumber+1, 1, 0)
        return_value, newVars, newFuncList, newCheckpointList, branchStr1, additionalStr = \
            run_code(codeList, lineNumber + 1, varList, funcList, checkpointList, endOfIf, "", False, multipleReturns)

        return_value2, newVars2, newFuncList2, newCheckpointList2, branchStr2, additionalStr2 = run_code(
            codeList, endOfIf, varList, funcList, checkpointList, endOfContext, "", funcCallInFunc, multipleReturns)

        branches = createBranches(varList, funcList, branchStr1, branchStr2, funcCallInFunc, multipleReturns)

        if compile_result.value == LESSER_THAN:
            branchCompare = "blt   .LBB" + str(len(funcList)) + "_1\n" \
                            "b     .LBB" + str(len(funcList)) + "_2"
            return IntReturn(0), varList, funcList, checkpointList, CommentedOutputStr+str_result+branchCompare, branches
        elif compile_result.value == GREATER_THAN:
            branchCompare = "bgt   .LBB" + str(len(funcList)) + "_1\n" \
                            "b     .LBB" + str(len(funcList)) + "_2"
            return IntReturn(0), varList, funcList, checkpointList, CommentedOutputStr+str_result+branchCompare, branches
        elif compile_result.value == IS_EQUAL_TO:
            branchCompare = "beq   .LBB" + str(len(funcList)) + "_1\n" \
                            "b     .LBB" + str(len(funcList)) + "_2"
            return IntReturn(0), varList, funcList, checkpointList, CommentedOutputStr+str_result+branchCompare, branches
        elif compile_result.value == GREATER_OR_EQUAL_TO:
            branchCompare = "bge   .LBB" + str(len(funcList)) + "_1\n" \
                            "b     .LBB" + str(len(funcList)) + "_2"
            return IntReturn(0), varList, funcList, checkpointList, CommentedOutputStr+str_result+branchCompare, branches
        elif compile_result.value == LESSER_OR_EQUAL_TO:
            branchCompare = "ble   .LBB" + str(len(funcList)) + "_1\n" \
                            "b     .LBB" + str(len(funcList)) + "_2"
            return IntReturn(0), varList, funcList, checkpointList, CommentedOutputStr+str_result+branchCompare, branches

    elif type(compile_result) == CheckpointReturn:  # If a checkpoint is returned, compile the contents

        newCheckpoint = Checkpoint(compile_result.value, str_result)
        return_value, newVars, newFuncList, newCheckpointList, returnStr, additionalStr = run_code(codeList,
        lineNumber + 1, varList, funcList, checkpointList + [newCheckpoint], endOfContext, "", False, multipleReturns)

        checkpointStr = str_result + ":\n" + addTabs(returnStr, 0, "") + "\n\n" + additionalStr

        return IntReturn(0), varList, funcList, checkpointList, CommentedOutputStr + "b     " + str_result, checkpointStr

    elif type(compile_result) == VarReturn:

        # Check if the variable already exists, if so replace it, if not add it to varList
        if checkIfNameInList(varList, compile_result.name):
            varNames = getListNames(varList, 0, [])
            storeLocation = varList[varNames.index(compile_result.name)].location
            if storeLocation == '0':
                storeStr = "str   r0, [sp]\n"
                return run_code(codeList, lineNumber + 1, varList, funcList, checkpointList, endOfContext, CommentedOutputStr +
                                str_result + "\n" + storeStr, funcCallInFunc, multipleReturns)

            storeStr = "str   r0, [sp, #" + storeLocation + "]\n"
            return run_code(codeList, lineNumber + 1, varList, funcList, checkpointList, endOfContext, CommentedOutputStr +
                            str_result + "\n" + storeStr, funcCallInFunc, multipleReturns)

        assignStr = "str   r0, [sp, #" + str(len(varList)*4) + "]\n"
        newOutputStr = CommentedOutputStr + str_result + "\n" + assignStr

        return run_code(codeList, lineNumber + 1, varList + [Variable(compile_result.name, str(len(varList)*4))],
                        funcList, checkpointList, endOfContext, newOutputStr, funcCallInFunc, multipleReturns)

    return run_code(codeList, lineNumber + 1, varList, funcList, checkpointList, endOfContext, CommentedOutputStr + str_result +
                    "\n", funcCallInFunc, multipleReturns)
