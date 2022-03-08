from Tokens import *
from typing import Union, Callable, Tuple

# =============== LEXER =====================


def return_numbers(text: str, index: int) -> str:
    if not index == len(text) and text[index].isdigit():
        return text[index] + return_numbers(text, index+1)
    return ''


def return_chars(text: str, index: int) -> str:
    if not index == len(text) and (text[index] != ' ' and text[index] != '\n'):
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


# =============== PARSER =====================

class TokenNode(NamedTuple):
    tok: Token


class OpNode(NamedTuple):
    left_node: 'Node'
    operator: Token
    right_node: 'Node'


Node = Union[TokenNode, OpNode]


def factor(tokens: list, index: int) -> Tuple[Node, int]:
    if tokens[index].type == NUMBER:
        return TokenNode(tokens[index]), index + 1

    elif tokens[index].type == OPEN_BRACKET:
        New_node, new_index = expression(tokens, index + 1)
        if tokens[new_index].type != CLOSE_BRACKET:
            raise Exception("Expected )")
        return New_node, new_index + 1

    else:
        raise Exception("Expected Int")


def term(tokens: list, index: int) -> Tuple[Node, int]:
    return operation(factor, MULTIPLY, tokens, index)


def expression(tokens: list, index: int) -> Tuple[Node, int]:
    return operation(term, [PLUS, MINUS], tokens, index)


def operationSearch(func: Callable, operators: list, tokens: list, index: int, left_node: Node) -> Tuple[Node, int]:
    if len(tokens) <= index:
        return left_node, index
    elif tokens[index].type not in operators:
        return left_node, index

    operator_token = tokens[index]
    right_node, new_index = func(tokens, index+1)

    return operationSearch(func, operators, tokens, new_index, OpNode(left_node, operator_token, right_node))


def operation(func: Callable, operators: list, tokens: list, index: int) -> Tuple[Node, int]:
    left, new_index = func(tokens, index)

    return operationSearch(func, operators, tokens, new_index, left)


def parseTokens(tokens: list, index: int) -> Node:
    result, unused_index = expression(tokens, index)
    return result

# =============== INTERPRETER =====================


class TreeInterpreter:
    def no_visit_method(self, node: Node):
        raise Exception(f'visit_{type(node).__name__} method is unknown')

    def visit(self, node: Node) -> int:
        method_name = f'visit_{type(node).__name__}'
        method = getattr(self, method_name, self.no_visit_method)
        return method(node)

    def visit_TokenNode(self, tokenNode: Node) -> int:
        return int(tokenNode.tok.value)

    def visit_OpNode(self, opNode: Node) -> int:
        left = self.visit(opNode.left_node)
        right = self.visit(opNode.right_node)

        if opNode.operator.type == PLUS:
            if isinstance(right, int):
                return left + right
        elif opNode.operator.type == MINUS:
            if isinstance(right, int):
                return left - right
        elif opNode.operator.type == MULTIPLY:
            if isinstance(right, int):
                return left * right
