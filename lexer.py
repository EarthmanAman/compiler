import string
from error import IllegalCharErrorExpectedCharError, InvalidSyntaxError, RTError
from position import Position
from constants import DIGITS, LETTERS, LETTERS_DIGITS
from keywords import KEYWORDS
from tokens import (TT_INT, TT_FLOAT, TT_PLUS, TT_MINUS, TT_MUL, TT_DIV, TT_STRING, TT_LEFT_PARENTHESIS, TT_RIGHT_PARENTHESIS, TT_LEFT_CURL_BRACES,
    TT_RIGHT_CURL_BRACES, TT_SEMICOLON, TT_FULLCOLON, TT_EQUAL_EQUAL, TT_NE, TT_LT, TT_GT, TT_LTE, TT_GTE, TT_LSQUAREBRACET, TT_RSQUAREBRACET, TT_COMMA, TT_IDENTIFIER, TT_KEYWORD, TT_EQ
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
                tokens.append(Token(TT_PLUS))
                self.advance()
            elif self.current_char == '-':
                tokens.append(Token(TT_MINUS))
                self.advance()
            elif self.current_char == '*':
                tokens.append(Token(TT_MUL))
                self.advance()
            elif self.current_char == '/':
                tokens.append(Token(TT_DIV))
                self.advance()
            elif self.current_char == '=':
                tokens.append(self.make_equals())
            elif self.current_char == '<':
                tokens.append(self.make_less_than())
            elif self.current_char == '>':
                tokens.append(self.make_greater_than())
                self.advance()
            elif self.current_char == '(':
                tokens.append(Token(TT_LEFT_PARENTHESIS))
                self.advance()
            elif self.current_char == ')':
                tokens.append(Token(TT_RIGHT_PARENTHESIS))
                self.advance()
            elif self.current_char == '{':
                tokens.append(Token(TT_LEFT_CURL_BRACES))
                self.advance()
            elif self.current_char == '}':
                tokens.append(Token(TT_RIGHT_CURL_BRACES))
                self.advance()
            elif self.current_char == '[':
                tokens.append(Token(TT_LSQUAREBRACET))
                self.advance()
            elif self.current_char == ']':
                tokens.append(Token(TT_RSQUAREBRACET))
                self.advance()
            elif self.current_char == ';':
                tokens.append(Token(TT_SEMICOLON))
                self.advance()
            elif self.current_char == ',':
                tokens.append(Token(TT_COMMA))
                self.advance()
            elif self.current_char == '.':
                tokens.append(Token(TT_KEYWORD, "."))
                self.advance()
            elif self.current_char == ':':
                tokens.append(Token(TT_FULLCOLON))
                self.advance()
            else:
                pos_start = self.pos.copy()
                char = self.current_char
                self.advance()
                return [], IllegalCharError(pos_start, self.pos, "'" + char + "'")

        return tokens, None

    def make_number(self):
        num_str = ''
        dot_count = 0
        
        while self.current_char != None and self.current_char in DIGITS + '.':
            if self.current_char == '.':
                if dot_count == 1: break
                dot_count += 1
                num_str += '.'
            else:
                num_str += self.current_char
            self.advance()

        if dot_count == 0:
            return Token(TT_INT, int(num_str))
        else:
            return Token(TT_FLOAT, float(num_str))

    def make_identifier(self, t=None):
        id_str = ''
        

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
        
        return Token(tok_type, id_str)

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
        return Token(TT_STRING, string)

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

        return Token(tok_type)

    def make_less_than(self):
        tok_type = TT_LT
        
        self.advance()

        if self.current_char == '=':
            self.advance()
            tok_type = TT_LTE

        return Token(tok_type)

    def make_greater_than(self):
        tok_type = TT_GT
        
        self.advance()

        if self.current_char == '=':
            self.advance()
            tok_type = TT_GTE

        return Token(tok_type)

#######################################
# NODES
#######################################



#######################################
# RUN
#######################################

def run(fn, text):
    lexer = Lexer(fn, text)
    tokens, error = lexer.make_tokens()

    return tokens, error, symbolTable