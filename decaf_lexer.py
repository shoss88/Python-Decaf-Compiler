reserved_words = {
    'boolean': 'BOOLEAN',
    'extends': 'EXTENDS',
    'new': 'NEW',
    'super': 'SUPER',
    'break': 'BREAK',
    'false': 'FALSE',
    'null': 'NULL',
    'this': 'THIS',
    'continue': 'CONTINUE',
    'float': 'FLOAT',
    'private': 'PRIVATE',
    'true': 'TRUE',
    'class': 'CLASS',
    'for': 'FOR',
    'public': 'PUBLIC',
    'void': 'VOID',
    'do': 'DO',
    'if': 'IF',
    'return': 'RETURN',
    'while': 'WHILE',
    'else': 'ELSE',
    'int': 'INT',
    'static': 'STATIC'
}

tokens = [
    'PLUS',
    'MINUS',
    'MULTIPLY',
    'DIVIDE',
    'INCREMENT',
    'DECREMENT',
    'INT_CONST',
    'FLOAT_CONST',
    'STRING',
    'ID',
    'COMMENT',
    'LCURLY',
    'RCURLY',
    'LPAREN',
    'RPAREN',
    'COMMA',
    'DOT',
    'SEMICOLON',
    'AND',
    'OR',
    'EQUAL_TO',
    'NOT_EQUAL_TO',
    'LESS_THAN',
    'GREATER_THAN',
    'LESS_OR_EQUAL_TO',
    'GREATER_OR_EQUAL_TO',
    'NEGATION',
    'ASSIGN_OP'
] + list(reserved_words.values())

t_PLUS = r'\+'
t_MINUS = r'-'
t_MULTIPLY = r'\*'
t_DIVIDE = r'/'
t_INCREMENT = r'\+\+'
t_DECREMENT = r'--'
t_FLOAT_CONST = r'[0-9]+\.[0-9]+'
t_INT_CONST = r'[0-9]+'
t_STRING = r'"[^"(\n)]*"'
t_LCURLY = r'{'
t_RCURLY = r'}'
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_COMMA = r','
t_DOT = r'\.'
t_SEMICOLON = r';'
t_AND = r'&&'
t_OR = r'\|\|'
t_EQUAL_TO = r'=='
t_NOT_EQUAL_TO = r'!='
t_LESS_THAN = r'<'
t_GREATER_THAN = r'>'
t_LESS_OR_EQUAL_TO = r'<='
t_GREATER_OR_EQUAL_TO = r'>='
t_NEGATION = r'!'
t_ASSIGN_OP = r'='


def t_ID(t):
    r'[a-zA-Z][a-zA-Z0-9_]*'
    t.type = reserved_words.get(t.value, 'ID')
    return t


def t_COMMENT(t):
    r'(//.*)|(/\*(.|\n)*?\*/)'
    pass


def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)


t_ignore = ' \t'


def t_error(t):
    column_num = t.lexpos - t.lexer.lexdata.rfind("\n", 0, t.lexpos) + 1
    print("Error: illegal character detected on line " + str(t.lexer.lineno) +
          ", column " + str(column_num))
    exit()
