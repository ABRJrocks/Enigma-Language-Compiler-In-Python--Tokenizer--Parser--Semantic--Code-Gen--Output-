import re

# Define the patterns for different lexical elements in the language
TOKEN_PATTERNS = [
    ('DATATYPE', r'\b(enum|efl|estr|ebool)\b'),
    ('BOOLEAN_VAL', r'\b(yup|nah)\b'),
    ('FUNCTION_DEF',
     r'\bf-(none|enum|efl|estr|ebool)\s+[a-zA-Z][_a-zA-Z0-9]*\b'),
    ('VARIABLE', r'\bv-[a-zA-Z][_a-zA-Z0-9]*\b'),
    ('NUMBER', r'\b\d+(\.\d+)?\b'),
    ('STRING', r'"[^"]*"'),
    ('COMMENT', r'//.*'),
    ('ASSIGN', r'='),
    ('OPERATOR', r'[\+\-\*/<>=!]+'),
    ('INCREMENT', r'\+\+'),  # Pattern to match the increment operator
    ('DECREMENT', r'--'),    # Pattern to match the decrement operator
    ('STATEMENT_TERMINATOR', r','),
    ('WHITESPACE', r'\s+'),
    ('NEWLINE', r'\n'),
    ('IFF', r'\biff\b'),
    ('MAYBE', r'\bmaybe\b'),
    ('ORELSE', r'\borelse\b'),
    ('ITERATE', r'\biterate\b'),
    ('WHILST', r'\bwhilst\b'),
    ('BR', r'\bbr\b'),
    ('CONT', r'\bcont\b'),
    ('LPAREN', r'\('),
    ('RPAREN', r'\)'),
    ('LCURLY', r'\{'),
    ('RCURLY', r'\}'),
    ('COMMA', r','),
    ('ERROR', r'.+'),
]

# Compile the regular expressions into a single pattern
TOKEN_REGEX = re.compile(
    '|'.join(f'(?P<{name}>{pattern})' for name, pattern in TOKEN_PATTERNS))


def tokenize(source_code):
    tokens = []
    errors = []
    line_num = 1
    line_start = 0

    for match in TOKEN_REGEX.finditer(source_code):
        kind = match.lastgroup
        value = match.group()
        column = match.start() - line_start + 1

        if kind == 'WHITESPACE' or kind == 'COMMENT':
            line_num += value.count('\n')
        elif kind == 'NEWLINE':
            line_num += 1
            line_start = match.end()
        else:
            if kind == 'ERROR':
                errors.append(
                    f"Error: Unexpected character(s) '{value}' at line {line_num}, column {column}")
            tokens.append({
                'type': kind,
                'value': value,
                'line': line_num,
                'column': column
            })

    return tokens, errors
