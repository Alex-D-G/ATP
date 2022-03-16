from Tokens import *
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


A = TypeVar('A')  # used mostly for varList
B = TypeVar('B')  # used mostly for checkpointList


# This functions collects all names from elements in a given list
def getListNames(varList: List[A], index: int, results: List[str]) -> List[str]:
    if index == len(varList):
        return results
    return getListNames(varList, index + 1, results + [varList[index].name])


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
def getVarsFromTokens(tokens: List[Token], index: int, varList: List[str]) -> List[Union[List[str], int]]:
    if tokens[index].type == CLOSE_BRACKET:
        return [varList, index]
    # if token is a number or a name (a variable) add it to the varlist
    elif tokens[index].type == NUMBER or tokens[index].type == NAME:
        return getVarsFromTokens(tokens, index + 1, varList + [tokens[index].value])
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
        varNames = getListNames(varList, 0, [])
        # Check if the name is a variable
        if tokens[index].value in varNames:
            if index + 1 != len(tokens):
                # Check if its assigning a new value to the variable, if not create a var call
                if tokens[index + 1].type == EQUAL:
                    New_node, new_index = expression(tokens, index + 2, varList, funcList)

                    return VarNode(tokens[index], New_node), new_index
            return TokenNode(tokens[index]), index + 1  # Var call

        # Check if  the name is a function
        funcNames = getListNames(funcList, 0, [])
        if tokens[index].value in funcNames:
            # Check if syntax is correct
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


# ========= INTERPRETER return types ==============


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
    value: bool


# This class is used for returning new checkpoints
class CheckpointReturn(NamedTuple):
    value: Token


# This class is used for returning a goTo's target
class GoToReturn(NamedTuple):
    value: int


# This Union allows functions to return multiple types of return
ReturnType = Union[IntReturn, VarReturn, FuncReturn, ReturnReturn, IfReturn, CheckpointReturn, GoToReturn]


# =============== INTERPRETER =====================


# Interpreter class, this class contains all functions needed for interpreting the parsed code
class TreeInterpreter:
    # This function send the node to the correct visit function
    def visit(self, node: Node, varList: List[A], funcList: List['FuncContext'],
              checkpointList: List[B], codeList: List[str]) -> ReturnType:

        # Create the method function's name
        method_name = f'visit_{type(node).__name__}'
        # Get the function
        method = getattr(self, method_name)
        return method(node, varList, funcList, checkpointList, codeList)

    # This function sends a list of nodes to the visit function
    def visit_list(self, toVisitList: List[Node], index: int, result: List[int], varList: List[A],
                   funcList: List['FuncContext'], checkpointList: List[B], codeList: List[str]) -> List[int]:
        # If the end of the list is reached, return the result
        if len(toVisitList) == index:
            return result
        # Visit the current index and add the value to result
        value = self.visit(toVisitList[index], varList, funcList, checkpointList, codeList)
        return self.visit_list(toVisitList, index + 1, result + [value.value],
                               varList, funcList, checkpointList, codeList)

    # This function returns a newly created function
    @staticmethod
    def visit_FuncCreateNode(funcNode: Node, varList: List[A], funcList: List['FuncContext'],
                             checkpointList: List[B], codeList: List[str]) -> ReturnType:

        return FuncReturn(funcNode.name, funcNode.varList)

    # This function returns the result of a called function
    def visit_FuncCallNode(self, funcNode: Node, varList: List[A], funcList: List['FuncContext'],
                           checkpointList: List[B], codeList: List[str]) -> ReturnType:

        funcNames = getListNames(funcList, 0, [])
        # If the called function exists, call it:
        if funcNode.name in funcNames:
            target_func = funcList[funcNames.index(str(funcNode.name))]
            # Check if the correct number of variables is provided
            if len(funcNode.varList) == len(target_func.varList):
                # Turn the provided variable nodes into usable variables
                new_vars = self.visit_list(funcNode.varList, 0, [], varList, funcList, checkpointList, codeList)

                # Merge function variables with global variables
                funcVarList = assignFunctionVariables(varList, target_func.varList, new_vars, 0, [])

                # Remove duplicate variables
                newVarList = applyFuncToList(removeTargetFromList, varList, funcVarList, 0)
                # Run the called function
                return_value, newVars, newFuncList, newCheckpointList = run_code(codeList, target_func.start + 1,
                                                                                 newVarList, funcList, checkpointList,
                                                                                 target_func.end)
                # Return the functions output
                return IntReturn(return_value.value)

    # This function returns a newly created checkpoint
    @staticmethod
    def visit_CheckpointNode(checkpointNode: Node, varList: List[A], funcList: List['FuncContext'],
                             checkpointList: List[B], codeList: List[str]) -> ReturnType:

        return CheckpointReturn(checkpointNode.name)

    # This function checks if the checkpoint given to the goTo exists, if so it returns its line number
    @staticmethod
    def visit_GoToNode(goToNode: Node, varList: List[A], funcList: List['FuncContext'],
                       checkpointList: List[B], codeList: List[str]) -> ReturnType:

        checkpointNames = getListNames(checkpointList, 0, [])
        # Check if the goTo's target exists, if so return its line number
        if goToNode.name in checkpointNames:
            return GoToReturn(checkpointList[checkpointNames.index(str(goToNode.name))].line)

    # This function returns the outcome of an if statement
    def visit_IfNode(self, ifNode: Node, varList: List[A], funcList: List['FuncContext'],
                     checkpointList: List[B], codeList: List[str]) -> ReturnType:
        # Calculate the if statements outcome
        value = self.visit(ifNode.value, varList, funcList, checkpointList, codeList)
        # Return the outcome
        return IfReturn(value.value)

    # This function returns the result of the node provided to the return node
    def visit_ReturnNode(self, returnNode: Node, varList: List[A], funcList: List['FuncContext'],
                         checkpointList: List[B], codeList: List[str]) -> ReturnType:

        value = self.visit(returnNode.value, varList, funcList, checkpointList, codeList)
        return ReturnReturn(value.value)

    # This function creates a new variable and returns it
    def visit_VarNode(self, varNode: Node, varList: List[A], funcList: List['FuncContext'],
                      checkpointList: List[B], codeList: List[str]) -> ReturnType:

        value = self.visit(varNode.value, varList, funcList, checkpointList, codeList)
        return VarReturn(varNode.name.value, value.value)

    # This function returns the value of a provided Token
    @staticmethod
    def visit_TokenNode(tokenNode: Node, varList: List[A], funcList: List['FuncContext'],
                        checkpointList: List[B], codeList: List[str]) -> ReturnType:
        # Check if the given token is a variable
        if tokenNode.tok.type == NAME:
            varNames = getListNames(varList, 0, [])
            # Check if the variable exists
            if tokenNode.tok.value in varNames:
                return IntReturn(varList[varNames.index(tokenNode.tok.value)].value)
        return IntReturn(int(tokenNode.tok.value))

    # This function calculates the outcome of a provided operator node
    def visit_OpNode(self, opNode: Node, varList: List[A], funcList: List['FuncContext'],
                     checkpointList: List[B], codeList: List[str]) -> ReturnType:
        # Calculate the value of the left node
        left = self.visit(opNode.left_node, varList, funcList, checkpointList, codeList)
        # Calculate the value of the right node
        right = self.visit(opNode.right_node, varList, funcList, checkpointList, codeList)

        # Perform the correct calculation based on the operator
        if opNode.operator.type == PLUS:
            return IntReturn(left.value + right.value)
        elif opNode.operator.type == MINUS:
            return IntReturn(left.value - right.value)
        elif opNode.operator.type == MULTIPLY:
            return IntReturn(left.value * right.value)
        elif opNode.operator.type == GREATER_THAN:
            return IntReturn(left.value > right.value)
        elif opNode.operator.type == LESSER_THAN:
            return IntReturn(left.value < right.value)
        elif opNode.operator.type == GREATER_OR_EQUAL_TO:
            return IntReturn(left.value >= right.value)
        elif opNode.operator.type == LESSER_OR_EQUAL_TO:
            return IntReturn(left.value <= right.value)
        elif opNode.operator.type == IS_EQUAL_TO:
            return IntReturn(left.value == right.value)


# =============== CONTROLLER =====================


# This function adds new function variables to the globalVarlist and overwrites existing variables
def assignFunctionVariables(varList: List[A], varNames: List[str], varValues: List[int],
                            index: int, assignedVars: List[A]) -> List[A]:
    # If the end of the varNames is reached, return the assigned variables
    if len(varNames) == index:
        return assignedVars

    varNamesList = getListNames(varList, 0, [])
    # Check if the current index is an existing variable
    if varValues[index] in varNamesList:
        # Overwrite the existing variable with its new value
        newVar = VarReturn(varNames[index], varList[varNames.index(varNames[index])].value)
        return assignFunctionVariables(varList, varNames, varValues, index + 1, assignedVars + [newVar])

    newVar = VarReturn(varNames[index], varValues[index])
    return assignFunctionVariables(varList, varNames, varValues, index + 1, assignedVars + [newVar])


# This function removes unique variables from a two provided varLists
# This function returns the combined lists minus the unique vars
def removeUniqueVars(oldVars: List[A], newVars: List[A], index: int, result: List[A]) -> List[A]:
    # Check if the end of newVars is reached, if so return result
    if len(newVars) == index:
        return result
    varNames = getListNames(oldVars, 0, [])
    # Check if the current index is an existing variable, if so add it to result
    if newVars[index].name in varNames:
        return removeUniqueVars(oldVars, newVars, index + 1, result + [newVars[index]])
    return removeUniqueVars(oldVars, newVars, index + 1, result)


# This Class holds all the information needed for a function
class FuncContext(NamedTuple):
    name: Token
    varList: List[A]
    start: int
    end: int


# This Class holds all the information needed for a checkpoint
class Checkpoint(NamedTuple):
    name: Token
    line: int


# This function is the main control function, it goes line for line through the code until an end is reached
def run_code(codeList: List[str], lineNumber: int, varList: List[A], funcList: List[FuncContext],
             checkpointList: List[B], endOfContext: int) -> Tuple[ReturnType, List[A], List[FuncContext], List[B]]:

    # Check if the end of the file is reached
    if len(codeList) == lineNumber:
        # Return 0, meaning there was no return found
        return IntReturn(0), varList, funcList, checkpointList
    # Check if the current line is empty
    elif codeList[lineNumber] == '\n':
        return run_code(codeList, lineNumber + 1, varList, funcList, checkpointList, endOfContext)
    # Check if the end of a context is reached
    elif endOfContext:
        if endOfContext - 1 == lineNumber:
            # Return 0, meaning there was no return found
            return IntReturn(0), varList, funcList, checkpointList

    # Call the Lexer
    tokens = getTokens(codeList[lineNumber], 0, [])

    # Call the Parser
    token_tree = parseTokens(tokens, 0, varList, funcList)

    # Create the Interpreter class
    inter = TreeInterpreter()
    # Call the Interpreter
    inter_result = inter.visit(token_tree, varList, funcList, checkpointList, codeList)

    # Check if the interpreter returned a new function, if so add it to funcList
    if type(inter_result) == FuncReturn:
        contextEnd = findEndOfContext(codeList, 0, lineNumber + 1, 1, 0)
        new_func = FuncContext(inter_result.name, inter_result.varList, lineNumber, contextEnd)
        return run_code(codeList, contextEnd, varList, funcList + [new_func], checkpointList, endOfContext)

    # Check if the interpreter returned a variable
    elif type(inter_result) == VarReturn:
        varNames = getListNames(varList, 0, [])
        # Check if the variable already exists, if so replace it, if not add it to varList
        if inter_result.name in varNames:
            new_varList = removeTargetFromList(varList, inter_result.name, 0, [])
            return run_code(codeList, lineNumber + 1, new_varList + [inter_result],
                            funcList, checkpointList, endOfContext)

        return run_code(codeList, lineNumber + 1, varList + [inter_result], funcList, checkpointList, endOfContext)

    # Check if the interpreter returned an if statement
    elif type(inter_result) == IfReturn:
        contextEnd = findEndOfContext(codeList, 0, lineNumber + 1, 1, 0)
        # Check if the statement returned true, if so run the code within it
        if inter_result.value:
            return_value, newVars, newFuncList, newCheckpointList = run_code(codeList,
                                                                             lineNumber + 1, varList, funcList,
                                                                             checkpointList, contextEnd)
            # If the if statement encountered a return statement, continue returning
            if type(return_value) == ReturnReturn:
                return return_value, varList, funcList, checkpointList
            # Continue with the code and remove any variables created in the if statement
            return run_code(codeList, contextEnd, removeUniqueVars(varList, newVars, 0, []),
                            funcList, checkpointList, endOfContext)
        return run_code(codeList, contextEnd, varList, funcList, checkpointList, endOfContext)

    # Check if the interpreter returned a checkpoint statement
    elif type(inter_result) == CheckpointReturn:
        checkpointNames = getListNames(checkpointList, 0, [])
        # Check if the checkpoint already exists, if so replace it
        if inter_result.value in checkpointNames:
            newCheckpointList = removeTargetFromList(checkpointList, str(inter_result.value), 0, [])
            newCheckpoint = Checkpoint(inter_result.value, lineNumber)
            return run_code(codeList, lineNumber + 1, varList, funcList,
                            newCheckpointList + [newCheckpoint], endOfContext)
        # Create a new checkpoint and add it to the list
        newCheckpoint = Checkpoint(inter_result.value, lineNumber)
        return run_code(codeList, lineNumber + 1, varList, funcList, checkpointList + [newCheckpoint], endOfContext)

    # Check if the interpreter returned a goTo statement
    elif type(inter_result) == GoToReturn:
        # Go to the goTo's target line
        return run_code(codeList, inter_result.value + 1, varList, funcList, checkpointList, endOfContext)

    # Check if the interpreter returned a return statement
    elif type(inter_result) == ReturnReturn:
        # Return alongside the result's value
        return ReturnReturn(inter_result.value), varList, funcList, checkpointList

    # Go another line
    return run_code(codeList, lineNumber + 1, varList, funcList, checkpointList, endOfContext)


# This function call a function in a provided codelist
def runFunc(codeList: List[str], funcName: str, funcVarList: List[A]) -> int:
    # Run the code in order to collect functions and global variables and checkpoints
    emptyValue, varList, funcList, checkpointList = run_code(codeList, 0, [], [], [], 0)

    funcNames = getListNames(funcList, 0, [])
    # Check if the called function exists
    if funcName in funcNames:
        # Get the called function from the function list
        targetFunc = funcList[funcNames.index(funcName)]

        # Assign the provided function variables
        funcVars = assignFunctionVariables(varList, targetFunc.varList, funcVarList, 0, [])

        # Run the function
        result, newVarList, newFuncList, newCheckpointList = \
            run_code(codeList, targetFunc.start + 1, funcVars, funcList, checkpointList, targetFunc.end)
        # Return its outcome
        return result.value
    return 0
