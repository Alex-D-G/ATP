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
            else:
                return getTokens(codeText, index + 1, lineNumber, result + [Token(GREATER_THAN, tmp_token)])

        elif tmp_token == '<':
            return getTokens(codeText, index + 1, lineNumber, result + [Token(LESSER_THAN, tmp_token)])

        elif tmp_token == '(':
            return getTokens(codeText, index + 1, lineNumber, result + [Token(OPEN_BRACKET, tmp_token)])

        elif tmp_token == ')':
            return getTokens(codeText, index + 1, lineNumber, result + [Token(CLOSE_BRACKET, tmp_token)])

        elif tmp_token == '=':
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


# =============== PARSER nodes =====================

class TokenNode(NamedTuple):
    tok: Token


class VarNode(NamedTuple):
    name: Token
    value: 'Node'


class PrintNode(NamedTuple):
    value: 'Node'


class OpNode(NamedTuple):
    left_node: 'Node'
    operator: Token
    right_node: 'Node'


Node = Union[TokenNode, OpNode, VarNode, PrintNode]

# =============== PARSER =====================


def getVariableNames(varList: list, index: int, results: list) -> list:
    if index == len(varList):
        return results
    return getVariableNames(varList, index+1, results + [varList[index].name])


def factor(tokens: list, index: int, varList: list) -> Tuple[Node, int]:
    if index == len(tokens):
        raise Exception("Syntax Error")

    elif tokens[index].type == NAME:
        varNames = getVariableNames(varList, 0, [])
        if tokens[index].value in varNames:
            return TokenNode(tokens[index]), index + 1

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

        New_node, new_index = expression(tokens, index + 3, varList)

        return VarNode(variable_name, New_node), new_index

    elif tokens[index].type == KEYWORD and tokens[index].value == 'print':
        if tokens[index+1].type == OPEN_BRACKET:
            New_node, new_index = expression(tokens, index + 2, varList)
            if tokens[new_index].type != CLOSE_BRACKET:
                raise Exception("Expected ')'")
            return PrintNode(New_node), new_index + 1
        raise Exception("Expected '('")

    elif tokens[index].type == NUMBER:
        return TokenNode(tokens[index]), index + 1

    elif tokens[index].type == OPEN_BRACKET:
        New_node, new_index = expression(tokens, index + 1, varList)
        if tokens[new_index].type != CLOSE_BRACKET:
            raise Exception("Expected )")
        return New_node, new_index + 1

    else:
        raise Exception("Expected Int")


def term(tokens: list, index: int, varList: list) -> Tuple[Node, int]:
    return operation(factor, MULTIPLY, tokens, index, varList)


def expression(tokens: list, index: int, varList: list) -> Tuple[Node, int]:

    return operation(term, [PLUS, MINUS], tokens, index, varList)


def operationSearch(func: Callable, operators: list, tokens: list, index: int, left_node: Node, varList: list) -> Tuple[Node, int]:
    if len(tokens) <= index:
        return left_node, index
    elif tokens[index].type not in operators:
        return left_node, index

    operator_token = tokens[index]
    right_node, new_index = func(tokens, index+1, varList)

    return operationSearch(func, operators, tokens, new_index, OpNode(left_node, operator_token, right_node), varList)


def operation(func: Callable, operators: list, tokens: list, index: int, varList: list) -> Tuple[Node, int]:
    left, new_index = func(tokens, index, varList)

    return operationSearch(func, operators, tokens, new_index, left, varList)


def parseTokens(tokens: list, index: int, varList: list) -> Node:
    result, unused_index = expression(tokens, index, varList)
    return result

# ========= INTERPRETER return types ==============


class VarReturn(NamedTuple):
    name: str
    value: int


class IntReturn(NamedTuple):
    value: int


ReturnType = Union[IntReturn, VarReturn]

# =============== INTERPRETER =====================


class TreeInterpreter:
    def no_visit_method(self, node: Node, varList: list):
        raise Exception(f'visit_{type(node).__name__} method is unknown')

    def visit(self, node: Node, varList: list) -> int:
        method_name = f'visit_{type(node).__name__}'
        method = getattr(self, method_name, self.no_visit_method)
        return method(node, varList)

    def visit_PrintNode(self, printNode: Node, varList: list):
        value = self.visit(printNode.value, varList)
        print(value)

    def visit_VarNode(self, varNode: Node, varList: list):
        value = self.visit(varNode.value, varList)
        return VarReturn(varNode.name.value, value)

    def visit_TokenNode(self, tokenNode: Node, varList: list) -> int:
        if tokenNode.tok.type == NAME:
            varNames = getVariableNames(varList, 0, [])
            if tokenNode.tok.value in varNames:
                return varList[varNames.index(tokenNode.tok.value)].value
        return int(tokenNode.tok.value)

    def visit_OpNode(self, opNode: Node, varList: list) -> int:
        left = self.visit(opNode.left_node, varList)
        right = self.visit(opNode.right_node, varList)

        if opNode.operator.type == PLUS:
            return left + right
        elif opNode.operator.type == MINUS:
            return left - right
        elif opNode.operator.type == MULTIPLY:
            return left * right

# =============== CONTROLLER =====================


def run_code(codeList: list, index: int, varList: list) -> int:

    # Lexer
    tokens = getTokens(codeList[index], 0, 1, [])
    #print(tokens, '\n-------')

    # Parser
    token_tree = parseTokens(tokens, 0, varList)
    #print(token_tree, '\n-------')

    # Interpreter
    inter = TreeInterpreter()
    inter_result = inter.visit(token_tree, varList)
    if len(codeList) == index+1:
        return inter_result
    elif type(inter_result) == VarReturn:
        return run_code(codeList, index + 1, varList + [inter_result])
    return run_code(codeList, index+1, varList)

