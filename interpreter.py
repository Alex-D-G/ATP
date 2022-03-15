from Tokens import *
from typing import Union, Callable, Tuple

# =============== LEXER =====================


def return_numbers(text: str, index: int) -> str:
    if not index == len(text) and text[index].isdigit():
        return text[index] + return_numbers(text, index+1)
    return ''


def return_chars(text: str, index: int) -> str:
    if not index == len(text) and (text[index].isdigit() or text[index].isalpha()):
        return text[index] + return_chars(text, index+1)
    return ''


def getTokens(codeText: str, index: int, lineNumber: int, result: list) -> list:
    if index == len(codeText):
        return result
    else:
        tmp_token = codeText[index]
        if tmp_token.isdigit():
            number = tmp_token + return_numbers(codeText, index+1)
            return getTokens(codeText, index + len(number), lineNumber, result + [Token(NUMBER, number)])

        elif tmp_token.isalpha():
            word = tmp_token + return_chars(codeText, index+1)
            if word in KEYWORDS:
                return getTokens(codeText, index + len(word), lineNumber, result + [Token(KEYWORD, word)])
            return getTokens(codeText, index + len(word), lineNumber, result + [Token(NAME, word)])

        elif tmp_token == ' ' or tmp_token == '\n':
            if tmp_token == '\n':
                return getTokens(codeText, index + 1, lineNumber+1, result)
            return getTokens(codeText, index + 1, lineNumber, result)

        elif tmp_token == '>':
            if (tmp_token + codeText[index+1] + codeText[index+2]) == '>>>':
                return getTokens(codeText, index + 3, lineNumber, result + [Token(GO_TO, '>>>')])
            elif (tmp_token + codeText[index+1]) == '>=':
                return getTokens(codeText, index + 2, lineNumber, result + [Token(IS_EQUAL_TO, '>=')])
            return getTokens(codeText, index + 1, lineNumber, result + [Token(GREATER_THAN, tmp_token)])

        elif tmp_token == '<':
            return getTokens(codeText, index + 1, lineNumber, result + [Token(LESSER_THAN, tmp_token)])

        elif tmp_token == '(':
            return getTokens(codeText, index + 1, lineNumber, result + [Token(OPEN_BRACKET, tmp_token)])

        elif tmp_token == ')':
            return getTokens(codeText, index + 1, lineNumber, result + [Token(CLOSE_BRACKET, tmp_token)])

        elif tmp_token == '{':
            return getTokens(codeText, index + 1, lineNumber, result + [Token(OPEN_C_BRACKET, tmp_token)])

        elif tmp_token == '}':
            return getTokens(codeText, index + 1, lineNumber, result + [Token(CLOSE_C_BRACKET, tmp_token)])

        elif tmp_token == '=':
            if (tmp_token + codeText[index+1]) == '==':
                return getTokens(codeText, index + 2, lineNumber, result + [Token(IS_EQUAL_TO, '==')])
            return getTokens(codeText, index + 1, lineNumber, result + [Token(EQUAL, tmp_token)])

        elif tmp_token == '-':
            if len(result) == 0:
                number = tmp_token + return_numbers(codeText, index + 1)
                return getTokens(codeText, index + len(number), lineNumber, result + [Token(NUMBER, number)])
            elif result[-1].type in [MINUS, PLUS, MULTIPLY, OPEN_BRACKET]:
                number = tmp_token + return_numbers(codeText, index + 1)
                return getTokens(codeText, index + len(number), lineNumber, result + [Token(NUMBER, number)])

            return getTokens(codeText, index + 1, lineNumber, result + [Token(MINUS, tmp_token)])

        elif tmp_token == '+':
            return getTokens(codeText, index + 1, lineNumber, result + [Token(PLUS, tmp_token)])

        elif tmp_token == '*':
            return getTokens(codeText, index + 1, lineNumber, result + [Token(MULTIPLY, tmp_token)])

        elif tmp_token == '?':
            return getTokens(codeText, index + 1, lineNumber, result + [Token(IF, tmp_token)])

        elif tmp_token == ',':
            return getTokens(codeText, index + 1, lineNumber, result + [Token(COMMA, tmp_token)])

        else:
            raise Exception("Unrecognized character \'" + tmp_token + "\' at line " + str(lineNumber))


# ========== List manipulation ===============

def getListNames(varList: list, index: int, results: list) -> list:
    if index == len(varList):
        return results
    return getListNames(varList, index+1, results + [varList[index].name])


def removeVariableFromList(varList: list, varName: str, index: int, newVarList: list) -> list:
    if index == len(varList):
        return newVarList
    if varList[index].name == varName:
        return removeVariableFromList(varList, varName, index+1, newVarList)
    return removeVariableFromList(varList, varName, index + 1, newVarList + [varList[index]])


def getVarsFromTokens(tokens: list, index: int, varList: list) -> list:
    if index == len(tokens):
        raise Exception("Expected ')'")
    elif tokens[index].type == CLOSE_BRACKET:
        return [varList, index]
    elif tokens[index].type == NAME:
        return getVarsFromTokens(tokens, index+1, varList + [tokens[index].value])
    elif tokens[index].type == NUMBER:
        return getVarsFromTokens(tokens, index+1, varList + [int(tokens[index].value)])
    elif tokens[index].type == COMMA:
        return getVarsFromTokens(tokens, index + 1, varList)
    raise Exception("Syntax Error")


def findEndOfContext(codeList: list, index: int, lineNumber: int, amountOpen: int, amountClosed: int) -> int:

    if amountOpen == amountClosed:
        return lineNumber
    elif lineNumber == len(codeList):
        raise Exception("Expected '}'")
    elif codeList[lineNumber][index] == '\n':
        return findEndOfContext(codeList, 0, lineNumber+1, amountOpen, amountClosed)
    elif codeList[lineNumber][index] == '}':
        return findEndOfContext(codeList, 0, lineNumber + 1, amountOpen, amountClosed + 1)
    elif codeList[lineNumber][index] == '{':
        return findEndOfContext(codeList, 0, lineNumber + 1, amountOpen + 1, amountClosed)
    return findEndOfContext(codeList, index + 1, lineNumber, amountOpen, amountClosed)

# =============== PARSER nodes =====================


class FuncCallNode(NamedTuple):
    name: Token
    varList: list


class FuncCreateNode(NamedTuple):
    name: Token
    varList: list


class TokenNode(NamedTuple):
    tok: Token


class VarNode(NamedTuple):
    name: Token
    value: 'Node'


class IfNode(NamedTuple):
    value: 'Node'


class PrintNode(NamedTuple):
    value: 'Node'


class ReturnNode(NamedTuple):
    value: 'Node'


class OpNode(NamedTuple):
    left_node: 'Node'
    operator: Token
    right_node: 'Node'


Node = Union[TokenNode, OpNode, VarNode, PrintNode, FuncCreateNode, FuncCallNode, ReturnNode, IfNode]


# =============== PARSER =====================

def factor(tokens: list, index: int, varList: list, funcList: list) -> Tuple[Node, int]:
    if index == len(tokens):
        raise Exception("Syntax Error")

    elif tokens[index].type == IF:
        if tokens[index + 1].type == OPEN_BRACKET and tokens[-2].type == CLOSE_BRACKET and tokens[-1].type == OPEN_C_BRACKET:
            New_node, new_index = comparison(tokens, index + 2, varList, funcList)
            return IfNode(New_node), new_index + 1

    elif tokens[index].type == NAME:
        varNames = getListNames(varList, 0, [])
        if tokens[index].value in varNames:
            if index + 1 != len(tokens):  # New Var
                if tokens[index + 1].type == EQUAL:
                    New_node, new_index = expression(tokens, index + 2, varList, funcList)

                    return VarNode(tokens[index], New_node), new_index
            return TokenNode(tokens[index]), index + 1  # Var call

        funcNames = getListNames(funcList, 0, [])
        if tokens[index].value in funcNames:   # Func call
            if tokens[index + 1].type == OPEN_BRACKET:
                new_vars = getVarsFromTokens(tokens, index + 2, [])
                return FuncCallNode(tokens[index].value, new_vars[0]), new_vars[1]+1

        raise Exception(tokens[index].value, " is unknown within this context")

    elif tokens[index].type == KEYWORD and tokens[index].value == 'var':
        if index+1 == len(tokens):
            raise Exception("Expected Variable Name")
        elif tokens[index+1].type != NAME:
            raise Exception("Expected Variable Name")
        variable_name = tokens[index+1]

        if index + 2 == len(tokens):
            raise Exception("Expected '='")
        elif tokens[index+2].type != EQUAL:
            raise Exception("Expected '='")

        New_node, new_index = expression(tokens, index + 3, varList, funcList)

        return VarNode(variable_name, New_node), new_index

    elif tokens[index].type == KEYWORD and tokens[index].value == 'print':
        if tokens[index+1].type == OPEN_BRACKET:
            New_node, new_index = expression(tokens, index + 2, varList, funcList)
            if tokens[new_index].type != CLOSE_BRACKET:
                raise Exception("Expected ')'")
            return PrintNode(New_node), new_index + 1
        raise Exception("Expected '('")

    elif tokens[index].type == KEYWORD and tokens[index].value == 'func':  # Function declaration
        if tokens[index + 1].type == NAME:
            if tokens[index + 2].type == OPEN_BRACKET and tokens[-2].type == CLOSE_BRACKET and tokens[-1].type == OPEN_C_BRACKET:
                return FuncCreateNode(tokens[index+1].value, getVarsFromTokens(tokens, index+3, [])[0]), len(tokens)
        raise Exception("Syntax Error")

    elif tokens[index].type == KEYWORD and tokens[index].value == 'return':
        New_node, new_index = expression(tokens, index + 1, varList, funcList)
        return ReturnNode(New_node), new_index

    elif tokens[index].type == NUMBER:
        return TokenNode(tokens[index]), index + 1

    elif tokens[index].type == OPEN_BRACKET:
        New_node, new_index = expression(tokens, index + 1, varList, funcList)
        if tokens[new_index].type != CLOSE_BRACKET:
            raise Exception("Expected )")
        return New_node, new_index + 1

    else:
        raise Exception("Expected Int")


def term(tokens: list, index: int, varList: list, funcList: list) -> Tuple[Node, int]:
    return operation(factor, MULTIPLY, tokens, index, varList, funcList)


def expression(tokens: list, index: int, varList: list, funcList: list) -> Tuple[Node, int]:
    return operation(term, [PLUS, MINUS], tokens, index, varList, funcList)


def comparison(tokens: list, index: int, varList: list, funcList: list) -> Tuple[Node, int]:
    return operation(factor, [LESSER_THAN, GREATER_THAN], tokens, index, varList, funcList)


def operationSearch(func: Callable, operators: list, tokens: list, index: int, left_node: Node, varList: list, funcList: list) -> Tuple[Node, int]:
    if len(tokens) <= index:
        return left_node, index
    elif tokens[index].type not in operators:
        return left_node, index

    operator_token = tokens[index]
    right_node, new_index = func(tokens, index+1, varList, funcList)

    return operationSearch(func, operators, tokens, new_index, OpNode(left_node, operator_token, right_node), varList, funcList)


def operation(func: Callable, operators: list, tokens: list, index: int, varList: list, funcList: list) -> Tuple[Node, int]:
    left, new_index = func(tokens, index, varList, funcList)

    return operationSearch(func, operators, tokens, new_index, left, varList, funcList)


def parseTokens(tokens: list, index: int, varList: list, funcList: list) -> Node:
    result, unused_index = expression(tokens, index, varList, funcList)
    return result

# ========= INTERPRETER return types ==============


class FuncReturn(NamedTuple):
    name: Token
    varList: list


class VarReturn(NamedTuple):
    name: str
    value: int


class IntReturn(NamedTuple):
    value: int


class ReturnReturn(NamedTuple):
    value: int


class IfReturn(NamedTuple):
    value: bool


ReturnType = Union[IntReturn, VarReturn, FuncReturn, ReturnReturn, IfReturn]

# =============== INTERPRETER =====================


class TreeInterpreter:
    def no_visit_method(self, node: Node, varList: list, funcList: list, codeList: list) -> ReturnType:
        raise Exception(f'visit_{type(node).__name__} method is unknown')

    def visit(self, node: Node, varList: list, funcList: list, codeList: list) -> ReturnType:
        method_name = f'visit_{type(node).__name__}'
        method = getattr(self, method_name, self.no_visit_method)
        return method(node, varList, funcList, codeList)

    def visit_FuncCreateNode(self, funcNode: Node, varList: list, funcList: list, codeList: list) -> ReturnType:
        return FuncReturn(funcNode.name, funcNode.varList)

    def visit_FuncCallNode(self, funcNode: Node, varList: list, funcList: list, codeList: list) -> ReturnType:
        funcNames = getListNames(funcList, 0, [])
        if funcNode.name in funcNames:

            target_func = funcList[funcNames.index(funcNode.name)]
            if len(funcNode.varList) == len(target_func.varList):
                funcVarList = assignFunctionVariables(varList, target_func.varList, funcNode.varList, 0, [])

                value, newVars = run_code(codeList, target_func.start + 1, varList + funcVarList, funcList, target_func.end)

                return IntReturn(value)
            raise Exception("Incorrect variable amount")

    def visit_PrintNode(self, printNode: Node, varList: list, funcList: list, codeList: list) -> ReturnType:
        value = self.visit(printNode.value, varList, funcList, codeList)
        print(value.value)
        return IntReturn(0)

    def visit_IfNode(self, ifNode: Node, varList: list, funcList: list, codeList: list) -> ReturnType:
        value = self.visit(ifNode.value, varList, funcList, codeList)

        return IfReturn(value.value)

    def visit_ReturnNode(self, printNode: Node, varList: list, funcList: list, codeList: list) -> ReturnType:
        value = self.visit(printNode.value, varList, funcList, codeList)
        return ReturnReturn(value.value)

    def visit_VarNode(self, varNode: Node, varList: list, funcList: list, codeList: list) -> ReturnType:
        value = self.visit(varNode.value, varList, funcList, codeList)
        return VarReturn(varNode.name.value, value.value)

    def visit_TokenNode(self, tokenNode: Node, varList: list, funcList: list, codeList: list) -> ReturnType:
        if tokenNode.tok.type == NAME:
            varNames = getListNames(varList, 0, [])
            if tokenNode.tok.value in varNames:
                return IntReturn(varList[varNames.index(tokenNode.tok.value)].value)
        return IntReturn(int(tokenNode.tok.value))

    def visit_OpNode(self, opNode: Node, varList: list, funcList: list, codeList: list) -> ReturnType:
        left = self.visit(opNode.left_node, varList, funcList, codeList)
        right = self.visit(opNode.right_node, varList, funcList, codeList)

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

# =============== CONTROLLER =====================


def assignFunctionVariables(varList: list, varNames: list, varValues: list, index: int, assignedVars: list) -> list:
    if len(varNames) == index:
        return assignedVars

    varNamesList = getListNames(varList, 0, [])
    if varValues[index] in varNamesList:
        newVar = VarReturn(varNames[index], varList[varNames.index(varNames[index])].value)
        return assignFunctionVariables(varList, varNames, varValues, index + 1, assignedVars + [newVar])

    newVar = VarReturn(varNames[index], varValues[index])
    return assignFunctionVariables(varList, varNames, varValues, index+1, assignedVars + [newVar])


def removeUniqueVars(oldVars: list, newVars: list, index: int, result: list) -> list:
    if len(newVars) == index:
        return result
    varNames = getListNames(oldVars, 0, [])
    if newVars[index].name in varNames:
        return removeUniqueVars(oldVars, newVars, index+1, result+[newVars[index]])
    return removeUniqueVars(oldVars, newVars, index + 1, result)


class FuncContext(NamedTuple):
    name: Token
    varList: list
    start: int
    end: int


def run_code(codeList: list, lineNumber: int, varList: list, funcList: list, endOfContext: int) -> Tuple[int, list]:
    if len(codeList) == lineNumber:
        return 1, varList  # Temporary
    elif codeList[lineNumber] == '\n':
        return run_code(codeList, lineNumber + 1, varList, funcList, endOfContext)
    elif endOfContext:
        if endOfContext-1 == lineNumber:
            return 0, varList

    # Lexer
    tokens = getTokens(codeList[lineNumber], 0, 1, [])
    # print(tokens, '\n-------')

    # Parser
    token_tree = parseTokens(tokens, 0, varList, funcList)
    # print(token_tree, '\n-------')

    # Interpreter
    inter = TreeInterpreter()
    inter_result = inter.visit(token_tree, varList, funcList, codeList)

    if type(inter_result) == FuncReturn:
        contextEnd = findEndOfContext(codeList, 0, lineNumber+1, 1, 0)
        new_func = FuncContext(inter_result.name, inter_result.varList, lineNumber, contextEnd)
        return run_code(codeList, contextEnd, varList, funcList + [new_func], endOfContext)

    elif type(inter_result) == VarReturn:
        varNames = getListNames(varList, 0, [])
        if inter_result.name in varNames:
            new_varList = removeVariableFromList(varList, inter_result.name, 0, [])
            return run_code(codeList, lineNumber + 1, new_varList + [inter_result], funcList, endOfContext)

        return run_code(codeList, lineNumber + 1, varList + [inter_result], funcList, endOfContext)

    elif type(inter_result) == IfReturn:
        contextEnd = findEndOfContext(codeList, 0, lineNumber + 1, 1, 0)
        if inter_result.value:
            value, newVars = run_code(codeList, lineNumber + 1, varList, funcList, contextEnd)

            return run_code(codeList, contextEnd + 1, removeUniqueVars(varList, newVars, 0, []), funcList, 0)
        return run_code(codeList, contextEnd + 1, varList, funcList, 0)

    elif type(inter_result) == ReturnReturn:
        return inter_result.value, varList

    return run_code(codeList, lineNumber+1, varList, funcList, endOfContext)
