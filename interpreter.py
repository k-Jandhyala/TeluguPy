import re

# Define token types
TOKEN_TYPES = {
    "KEYWORD": "KEYWORD",
    "IDENTIFIER": "IDENTIFIER",
    "OPERATOR": "OPERATOR",
    "STRING": "STRING",
    "NUMBER": "NUMBER",
    "PAREN": "PAREN",
    "NEWLINE": "NEWLINE",
}

# Keywords and operators
KEYWORDS = {'False', 'None', 'True',"__peg_parser__",'and', 'as', 'assert', 'async', 'await', 'break', 
'class', 'continue', 'def', 'del', 'elif', 'else', 'except', 'finally', 'for', 'from', 'global', 'if', 
'import', 'in', 'is', 'lambda', 'nonlocal', 'not', 'or', 'pass', 'raise', 'return', 'try', 'while', 'with', 'yield'}
OPERATORS = {"=", "==", "+", "-", "*", "/", "(", ")", "{", "}", ":"}

# Token class
class Token:
    def __init__(self, type_, value):
        self.type = type_
        self.value = value

    def __repr__(self):
        return f"Token({self.type}, {self.value})"


class CustomTokenizer:
    def __init__(self, code):
        self.code = code
        self.position = 0
        self.tokens = []

    def tokenize(self):
        while self.position < len(self.code):
            current_char = self.code[self.position]

            # Skip whitespaces
            if current_char.isspace():
                if current_char == "\n":
                    self.tokens.append(Token(TOKEN_TYPES["NEWLINE"], "\\n"))
                self.position += 1
                continue

            # Match keywords, identifiers (including Telugu characters)
            if current_char.isalpha() or self.is_telugu_char(current_char):
                token = self._tokenize_identifier_or_keyword()
                self.tokens.append(token)
                continue

            # Match operators
            if current_char in OPERATORS:
                token = self._tokenize_operator()
                self.tokens.append(token)
                continue

            # Match numbers
            if current_char.isdigit():
                token = self._tokenize_number()
                self.tokens.append(token)
                continue

            # Match string literals
            if current_char == '"':
                token = self._tokenize_string()
                self.tokens.append(token)
                continue

            self.position += 1  # Move to the next character

        return self.tokens

    def _tokenize_identifier_or_keyword(self):
        start_position = self.position
        while self.position < len(self.code) and (
            self.code[self.position].isalpha()
            or self.is_telugu_char(self.code[self.position])
        ):
            self.position += 1

        value = self.code[start_position : self.position]
        token_type = (
            TOKEN_TYPES["KEYWORD"] if value in KEYWORDS else TOKEN_TYPES["IDENTIFIER"]
        )
        return Token(token_type, value)

    def _tokenize_operator(self):
        value = self.code[self.position]
        self.position += 1
        return Token(TOKEN_TYPES["OPERATOR"], value)

    def _tokenize_number(self):
        start_position = self.position
        while self.position < len(self.code) and self.code[self.position].isdigit():
            self.position += 1

        value = self.code[start_position : self.position]
        return Token(TOKEN_TYPES["NUMBER"], value)

    def _tokenize_string(self):
        self.position += 1  # Skip the opening quote
        start_position = self.position

        while self.position < len(self.code) and self.code[self.position] != '"':
            self.position += 1

        value = self.code[start_position : self.position]
        self.position += 1  # Skip the closing quote
        return Token(TOKEN_TYPES["STRING"], value)

    def is_telugu_char(self, char):
        # Telugu Unicode range: U+0C00 to U+0C7F
        return "\u0C00" <= char <= "\u0C7F"


# Define AST Node classes
class ASTNode:
    pass

class VarAssign(ASTNode):
    def __init__(self, var_name, value):
        self.var_name = var_name
        self.value = value

class IfNode(ASTNode):
    def __init__(self, condition, body):
        self.condition = condition
        self.body = body

class PrintNode(ASTNode):
    def __init__(self, expression):
        self.expression = expression


# Parser to build an AST from the token list
class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.position = 0
        self.current_token = self.tokens[self.position]

    def _advance(self):
        self.position += 1
        if self.position < len(self.tokens):
            self.current_token = self.tokens[self.position]
        else:
            self.current_token = None

    def parse(self):
        statements = []
        while self.current_token is not None:
            if self.current_token.type == "IDENTIFIER" and self._peek().value == "=":
                statements.append(self._parse_var_assign())
            elif self.current_token.type == "KEYWORD" and self.current_token.value == "if":
                statements.append(self._parse_if())
            elif self.current_token.type == "IDENTIFIER" and self.current_token.value == "print":
                statements.append(self._parse_print())
            self._advance()  # Skip the token once processed
        return statements

    def _peek(self):
        if self.position + 1 < len(self.tokens):
            return self.tokens[self.position + 1]
        return None

    def _parse_var_assign(self):
        var_name = self.current_token.value
        self._advance()  # Skip variable name
        self._advance()  # Skip '='
        value = self.current_token.value
        return VarAssign(var_name, value)

    def _parse_if(self):
        self._advance()  # Skip 'if'
        self._advance()  # Skip '('
        condition = self.current_token.value
        self._advance()  # Skip the condition
        self._advance()  # Skip ')'
        self._advance()  # Skip ':'
        body = self.parse()  # Parse the body recursively
        return IfNode(condition, body)

    def _parse_print(self):
        self._advance()  # Skip 'print'
        self._advance()  # Skip '('
        expression = self.current_token.value
        self._advance()  # Skip expression
        return PrintNode(expression)


# Interpreter to execute the AST
class Interpreter:
    def __init__(self):
        self.variables = {}

    def interpret(self, node):
        if isinstance(node, VarAssign):
            self.variables[node.var_name] = node.value
        elif isinstance(node, IfNode):
            condition = self.variables.get(node.condition, False)
            if condition:
                for stmt in node.body:
                    self.interpret(stmt)
        elif isinstance(node, PrintNode):
            print(self.variables.get(node.expression, node.expression))


if __name__ == "__main__":
    # Read the code from code.txt file
    with open("code.txt", "r", encoding="utf-8") as f:
        code = f.read()

    tokenizer = CustomTokenizer(code)
    tokens = tokenizer.tokenize()

    # Parse the tokens into an AST
    parser = Parser(tokens)
    ast = parser.parse()

    # Interpret the AST
    interpreter = Interpreter()
    for node in ast:
        interpreter.interpret(node)
