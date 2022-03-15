from typing import NamedTuple

# TOKENS
GO_TO               = 'GO_TO'
LESSER_THAN         = 'LESSER_THAN'
GREATER_THAN        = 'GREATER_THAN'
IS_EQUAL_TO         = 'IS_EQUAL_TO'
GREATER_OR_EQUAL_TO = 'GREATER_OR_EQUAL_TO'
LESSER_OR_EQUAL_TO  = 'LESSER_OR_EQUAL_TO'
OPEN_BRACKET        = 'OPEN_BRACKET'
CLOSE_BRACKET       = 'CLOSE_BRACKET'
OPEN_C_BRACKET      = 'OPEN_C_BRACKET'
CLOSE_C_BRACKET     = 'CLOSE_C_BRACKET'
EQUAL               = 'EQUAL'
MINUS               = 'MINUS'
PLUS                = 'PLUS'
MULTIPLY            = 'MULTIPLY'
IF                  = 'IF'
EOF                 = 'EOF'
COMMA               = 'COMMA'
KEYWORD             = 'KEYWORD'
NAME                = 'NAME'
NUMBER              = 'NUMBER'

KEYWORDS = [  # Keywords that the language supports
    'var',
    'func',
    'checkpoint',
    'print',
    'return'
]


class Token(NamedTuple):
    type: str
    value: str
