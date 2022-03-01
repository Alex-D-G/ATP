from typing import NamedTuple
# TOKENS

DIVIDE          = 'DIVIDE'
GO_TO           = 'GO_TO'
GREATER_THAN    = 'GREATER_THAN'
LESSER_THAN     = 'LESSER_THAN'
OPEN_BRACKET    = 'OPEN_BRACKET'
CLOSE_BRACKET   = 'CLOSE_BRACKET'
EQUAL           = 'EQUAL'
MINUS           = 'MINUS'
PLUS            = 'PLUS'
MULTIPLY        = 'MULTIPLY'
IF              = 'IF'
EOF             = 'EOF'
COMMA           = 'COMMA'
INT             = 'INT'
WORD            = 'WORD'

#Keywords:
# 'checkpoint'


class Token(NamedTuple):
    type: str
    value: str
