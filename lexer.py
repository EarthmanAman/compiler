import string
from error import IllegalCharError, ExpectedCharError, InvalidSyntaxError, RTError
from position import Position
from constants import DIGITS, LETTERS, LETTERS_DIGITS
from keywords import KEYWORDS
from tokens import (TT_INT, TT_FLOAT, TT_PLUS, TT_MINUS, TT_MUL, TT_DIV, TT_STRING, TT_LEFT_PARENTHESIS, TT_RIGHT_PARENTHESIS, TT_LEFT_CURL_BRACES,
    TT_RIGHT_CURL_BRACES, TT_SEMICOLON, TT_FULLCOLON, TT_EQUAL_EQUAL, TT_NE, TT_LT, TT_GT, TT_LTE, TT_GTE, TT_LSQUAREBRACET, TT_RSQUAREBRACET, TT_COMMA, TT_IDENTIFIER, TT_KEYWORD, TT_EQ, TT_EOF,
    )
from token import Token

#######################################
# LEXER
#######################################
symbolTable = {}

class Lexer:
    def __init__(self, fn, text):
        self.fn = fn
        self.text = text
        self.pos = Position(-1, 0, -1, fn, text)
        self.current_char = None
        self.advance()
    
    def advance(self):
        self.pos.advance(self.current_char)
        self.current_char = self.text[self.pos.idx] if self.pos.idx < len(self.text) else None

    def make_tokens(self):
        tokens = []

        while self.current_char != None:
            if self.current_char in ' \t\n':
                self.advance()
            elif self.current_char in DIGITS:
                tokens.append(self.make_number())

            elif self.current_char in LETTERS:

                if len(tokens) == 0:
                    tokens.append(self.make_identifier())
                else:
                    tokens.append(self.make_identifier(tokens[-1]))

            elif self.current_char == '"':
                tokens.append(self.make_string())
            elif self.current_char == '!':
                self.make_comment()
            elif self.current_char == '+':
                tokens.append(Token(TT_PLUS, pos_start=self.pos))
                self.advance()
            elif self.current_char == '-':
                tokens.append(Token(TT_MINUS, pos_start=self.pos))
                self.advance()
            elif self.current_char == '*':
                tokens.append(Token(TT_MUL, pos_start=self.pos))
                self.advance()
            elif self.current_char == '/':
                tokens.append(Token(TT_DIV, pos_start=self.pos))
                self.advance()
            elif self.current_char == '=':
                tokens.append(self.make_equals())
            elif self.current_char == '<':
                tokens.append(self.make_less_than())
            elif self.current_char == '>':
                tokens.append(self.make_greater_than())
                self.advance()
            elif self.current_char == '(':
                tokens.append(Token(TT_LEFT_PARENTHESIS, pos_start=self.pos))
                self.advance()
            elif self.current_char == ')':
                tokens.append(Token(TT_RIGHT_PARENTHESIS, pos_start=self.pos))
                self.advance()
            elif self.current_char == '{':
                tokens.append(Token(TT_LEFT_CURL_BRACES, pos_start=self.pos))
                self.advance()
            elif self.current_char == '}':
                tokens.append(Token(TT_RIGHT_CURL_BRACES, pos_start=self.pos))
                self.advance()
            elif self.current_char == '[':
                tokens.append(Token(TT_LSQUAREBRACET, pos_start=self.pos))
                self.advance()
            elif self.current_char == ']':
                tokens.append(Token(TT_RSQUAREBRACET, pos_start=self.pos))
                self.advance()
            elif self.current_char == ';':
                tokens.append(Token(TT_SEMICOLON, pos_start=self.pos))
                self.advance()
            elif self.current_char == ',':
                tokens.append(Token(TT_COMMA, pos_start=self.pos))
                self.advance()
            elif self.current_char == '.':
                tokens.append(Token(TT_KEYWORD, ".", pos_start=self.pos))
                self.advance()
            elif self.current_char == ':':
                tokens.append(Token(TT_FULLCOLON, pos_start=self.pos))
                self.advance()
            else:
                pos_start = self.pos.copy()
                char = self.current_char
                self.advance()
                return [], IllegalCharError(pos_start, self.pos, "'" + char + "'")
        tokens.append(Token(TT_EOF, pos_start=self.pos))
        return tokens, None

    def make_number(self):
        num_str = ''
        dot_count = 0
        pos_start = self.pos.copy()

        while self.current_char != None and self.current_char in DIGITS + '.':
            if self.current_char == '.':
                if dot_count == 1: break
                dot_count += 1
                num_str += '.'
            else:
                num_str += self.current_char
            self.advance()

        if dot_count == 0:
            return Token(TT_INT, int(num_str), pos_start, self.pos)
        else:
            return Token(TT_FLOAT, float(num_str), pos_start, self.pos)

    def make_identifier(self, t=None):
        id_str = ''
        pos_start = self.pos

        while self.current_char != None and self.current_char in LETTERS_DIGITS + "_":
            id_str += self.current_char
            self.advance()
        if id_str in KEYWORDS:
            tok_type = TT_KEYWORD
        else:
            tok_type = TT_IDENTIFIER
            if id_str in symbolTable:
                id_str = symbolTable[id_str]["location"]
            else:
                if t == None:
                    symbolTable[id_str] = {"name":id_str, "location":len(symbolTable), "address":hex(id(id_str)), "dataType":"Initial"}
                else:
                    symbolTable[id_str] = {"name":id_str, "location":len(symbolTable), "address":hex(id(id_str)), "dataType":t}
                id_str = len(symbolTable)
        
        return Token(tok_type, id_str, pos_start, self.pos)

    def make_string(self):
        string = ''
        pos_start = self.pos.copy()
        escape_character = False
        self.advance()

        escape_characters = {
            'n': '\n',
            't': '\t'
        }

        while self.current_char != None and (self.current_char != '"' or escape_character):
            if escape_character:
                string += escape_characters.get(self.current_char, self.current_char)
            else:
                if self.current_char == '\\':
                    escape_character = True
                else:
                    string += self.current_char
            self.advance()
            escape_character = False
        
        self.advance()
        return Token(TT_STRING, string, pos_start, self.pos)

    def make_comment(self):
        string = ''
        pos_start = self.pos.copy()
        escape_character = False
        self.advance()

        while self.current_char != None and (self.current_char != '!' ):
          
            string += self.current_char
            self.advance()
            escape_character = False
        
        self.advance()
        return None
    def make_equals(self):
        tok_type = TT_EQ
        
        self.advance()

        if self.current_char == '=':
            self.advance()
            tok_type = TT_EQUAL_EQUAL

        return Token(tok_type, pos_start=self.pos)

    def make_less_than(self):
        tok_type = TT_LT
        
        self.advance()

        if self.current_char == '=':
            self.advance()
            tok_type = TT_LTE

        return Token(tok_type, pos_start=self.pos)

    def make_greater_than(self):
        tok_type = TT_GT
        
        self.advance()

        if self.current_char == '=':
            self.advance()
            tok_type = TT_GTE

        return Token(tok_type, pos_start=self.pos)

#######################################
# NODES
#######################################
class NumberNode:
    def __init__(self, tok):
        self.tok = tok

        self.pos_start = self.tok.pos_start
        self.pos_end = self.tok.pos_end

    def __repr__(self):
        return f'{self.tok}'


class NumberAccessNode:
    def __init__(self, Number_name_tok):
        self.Number_name_tok = Number_name_tok

        self.pos_start = self.Number_name_tok.pos_start
        self.pos_end = self.Number_name_tok.pos_end
    def __repr__(self):
        return f'{self.Number_name_tok}'

class NumberAssignNode:
    def __init__(self, Number_name_tok, value_node):
        self.Number_name_tok = Number_name_tok
        self.value_node = value_node

        self.pos_start = self.Number_name_tok.pos_start
        self.pos_end = self.value_node.pos_end
    def __repr__(self):
        return f'{self.Number_name_tok} = {self.value_node}'

class BinOpNode:
    def __init__(self, left_node, op_tok, right_node):
        self.left_node = left_node
        self.op_tok = op_tok
        self.right_node = right_node

        self.pos_start = self.left_node.pos_start
        self.pos_end = self.right_node.pos_end

    def __repr__(self):
        return f'({self.left_node}, {self.op_tok}, {self.right_node})'
class HeadNode:
    def __init__(self,left_node, op_tok, right_node):
        
        self.op_tok = op_tok
        self.left_node = left_node
        self.right_node = right_node
        self.pos_start = self.op_tok.pos_start
        self.pos_end = self.op_tok.pos_end

    def __repr__(self):
        
        return f'({self.left_node}) ({self.op_tok}) ({self.right_node})'

class UnaryOpNode:
    def __init__(self, op_tok, node):
        self.op_tok = op_tok
        self.node = node

        self.pos_start = self.op_tok.pos_start
        self.pos_end = node.pos_end

    def __repr__(self):
        return f'({self.op_tok}, {self.node})'

#######################################
# PARSE RESULT
#######################################

class ParseResult:
    def __init__(self):
        self.error = None
        self.node = None
        self.advance_count = 0

    def register_advancement(self):
        self.advance_count += 1

    def register(self, res):
        self.advance_count += res.advance_count
        if res.error: self.error = res.error
        return res.node

    def success(self, node):
        self.node = node
        return self

    def failure(self, error):
        if not self.error or self.advance_count == 0:
            self.error = error
        return self

#######################################
# PARSER
#######################################

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.tok_idx = -1
        self.advance()

    def advance(self, ):
        self.tok_idx += 1
        if self.tok_idx < len(self.tokens):
            self.current_tok = self.tokens[self.tok_idx]
        return self.current_tok

    def parse(self):
        res = self.head()
        res.register_advancement()
        self.advance()


        return res

    ###################################
    def atom(self):
        res = ParseResult()
        tok = self.current_tok

        if tok.type in (TT_INT, TT_FLOAT):
            res.register_advancement()
            self.advance()
            return res.success(NumberNode(tok))

        elif tok.type == TT_IDENTIFIER:
            res.register_advancement()
            self.advance()
            return res.success(NumberAccessNode(tok))

        elif tok.type == TT_LEFT_PARENTHESIS:
            res.register_advancement()
            self.advance()
            expr = res.register(self.expr())
            if res.error: return res
            if self.current_tok.type == TT_RIGHT_PARENTHESIS:
                res.register_advancement()
                self.advance()
                return res.success(expr)
            else:
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    "Expected ')'"
                ))

        return res.failure(InvalidSyntaxError(
            tok.pos_start, tok.pos_end,
            "Expected int, float, identifier, '+', '-' or '('"
        ))

    def factor(self):
        res = ParseResult()
        tok = self.current_tok

        if tok.type in (TT_PLUS, TT_MINUS):
            res.register_advancement()
            self.advance()
            factor = res.register(self.factor())
            if res.error: return res
            return res.success(UnaryOpNode(tok, factor))
        
        elif tok.type in (TT_INT, TT_FLOAT):
            res.register_advancement()
            self.advance()
            return res.success(NumberNode(tok))

        elif tok.type == TT_LEFT_PARENTHESIS:
            res.register_advancement()
            self.advance()
            expr = res.register(self.expr())
            if res.error: return res
            if self.current_tok.type == TT_RIGHT_PARENTHESIS:
                res.register(self.advance())
                return res.success(expr)
            else:
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    "Expected ')'"
                ))

        return res.failure(InvalidSyntaxError(
            tok.pos_start, tok.pos_end,
            "Expected int or float"
        ))

    def term(self):
        return self.bin_op(self.factor, (TT_MUL, TT_DIV))
   
    def head(self):
        res = ParseResult()
        if self.current_tok.getValue() == "HEAD":
            headStr = self.current_tok
            if res.error: 
                return res
            res.register_advancement()
            self.advance()
            left_node = None
            right_node = None
            body = None
            if self.current_tok.getValue() != None:
                newTokens = []
                bodyIndex = None
                for index, token in enumerate(self.tokens):
                    if token.getValue() == "BODY":
                        body = self.tokens[index + 1:]
                        bodyIndex = index
                        break
                    else:
                        newTokens.append(token)
                self.tokens = newTokens[:]
                left_node = res.register(self.expr())
                
                self.tokens = body[:]
                res.register_advancement()
                self.advance()
                
                right_node = res.register(self.expr())
            return res.success(HeadNode(left_node, headStr, right_node))

        else:
            return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    "Expected 'HEAD'"
                ))

    def expr(self):
        res = ParseResult()

        if self.current_tok.matches("IDENTIFIER"):
            Number_name = self.current_tok
            res.register_advancement()
            self.advance()

            

            if self.current_tok.type != TT_EQ:
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    "Expected '='"
                ))

            res.register_advancement()
            self.advance()
            expr = res.register(self.expr())
            if res.error: return res
            return res.success(NumberAssignNode(Number_name, expr))

        node = res.register(self.bin_op(self.term, (TT_PLUS, TT_MINUS)))

        if res.error:
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                "Expected 'Number', int, float, identifier, '+', '-' or '('"
            ))

        return res.success(node)

    ###################################

    def bin_op(self, func, ops):
        res = ParseResult()
        left = res.register(func())
        if res.error: return res

        while self.current_tok.type in ops:
            op_tok = self.current_tok
            res.register_advancement()
            self.advance()
            right = res.register(func())
            if res.error: return res
            left = BinOpNode(left, op_tok, right)

        return res.success(left)

#######################################
# RUN
#######################################

def run(fn, text):
    lexer = Lexer(fn, text)
    tokens, error = lexer.make_tokens()
    if error:return None, error

    #Generate AST
    parser = Parser(tokens)
    ast = parser.parse()
    return ast.node, ast.error, symbolTable