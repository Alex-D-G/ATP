from Tokens import *
from typing import Union, Callable, Tuple

# =============== LEXER =====================


def return_numbers(text: str, index: int) -> str:
    if not index == len(text) and text[index].isdigit():
        return text[index] + return_numbers(text, index+1)
    return ''


def return_chars(text: str, index: int) -> str:
    if not index == len(text) and text[index].isalpha():
        return text[index] + return_chars(text, index+1)
    return ''


def getTokens(codeText: str, index: int, lineNumber: int, result: list) -> list:
    if index == len(codeText):
        return result
    else:
        tmp_token = codeText[index]
        if tmp_token.isdigit():
            number = tmp_token + return_numbers(codeText, index+1)
            return getTokens(codeText, index + len(number), lineNumber, result + [Token(INT, number)])

        elif tmp_token.isalpha():
            keyword = tmp_token + return_chars(codeText, index+1)
            return getTokens(codeText, index + len(keyword), lineNumber, result + [Token(WORD, keyword)])

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

        elif tmp_token == '/':
            return getTokens(codeText, index + 1, lineNumber, result + [Token(DIVIDE, tmp_token)])

        elif tmp_token == '(':
            return getTokens(codeText, index + 1, lineNumber, result + [Token(OPEN_BRACKET, tmp_token)])

        elif tmp_token == ')':
            return getTokens(codeText, index + 1, lineNumber, result + [Token(CLOSE_BRACKET, tmp_token)])

        elif tmp_token == '=':
            return getTokens(codeText, index + 1, lineNumber, result + [Token(EQUAL, tmp_token)])

        elif tmp_token == '-':
            if result[-1].type in [MINUS, PLUS, DIVIDE, MULTIPLY]:
                number = tmp_token + return_numbers(codeText, index + 1)
                return getTokens(codeText, index + len(number), lineNumber, result + [Token(INT, number)])

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


class DubbelOpNode(NamedTuple):
    left_node: 'Node'
    operator: Token
    right_node: 'Node'


Node = Union[TokenNode, DubbelOpNode]


def factor(tokens: list, index: int) -> Tuple[Node, int]:
    if tokens[index].type == INT:
        return TokenNode(tokens[index]), index + 1

    elif tokens[index].type == OPEN_BRACKET:
        New_node, new_index = expression(tokens, index + 1)
        if tokens[new_index].type != CLOSE_BRACKET:
            raise Exception("Expected )")
        return New_node, new_index + 1

    else:
        raise Exception("Expected Int")


def term(tokens: list, index: int) -> Tuple[Node, int]:
    return operation(factor, [MULTIPLY, DIVIDE], tokens, index)


def expression(tokens: list, index: int) -> Tuple[Node, int]:
    return operation(term, [PLUS, MINUS], tokens, index)


def operationSearch(func: Callable, operators: list, tokens: list, index: int, left_node: Node) -> Tuple[Node, int]:
    if len(tokens) <= index:
        return left_node, index
    elif tokens[index].type not in operators:
        return left_node, index

    operator_token = tokens[index]
    right_node, new_index = func(tokens, index+1)

    return operationSearch(func, operators, tokens, new_index, DubbelOpNode(left_node, operator_token, right_node))


def operation(func: Callable, operators: list, tokens: list, index: int) -> Tuple[Node, int]:
    left, new_index = func(tokens, index)

    return operationSearch(func, operators, tokens, new_index, left)


def parseTokens(tokens: list, index: int) -> Node:
    result, unused_index = expression(tokens, index)
    return result
