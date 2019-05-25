import plex
import pdb

class ParseError(Exception):
    pass

class RunTimeError(Exception):
    pass

class myParser:
    def __init__(self):
        DIGIT = plex.Range("09")
        LETTER = plex.Range('azAZ')
        NUMBER = plex.Rep1(plex.Any('01'))
        IDENTIFIER_TOKEN_OPERATOR = LETTER + plex.Rep(LETTER|DIGIT)
        XOR_OPERATOR = plex.Str("^")
        OR_OPERATOR = plex.Str("|")
        AND_OPERATOR = plex.Str("&")
        EQUALITY_OPERATOR = plex.Str("=")
        OPEN_PARENTHESES = plex.Str("(")
        CLOSE_PARENTHESES = plex.Str(")")
        PRINT_TOKEN = plex.Str("print")
        SPACE = plex.Any(" \n\t")

        self.LEXICON = plex.Lexicon([(SPACE, plex.IGNORE),
                                     (NUMBER, "NUMBER"),
                                     (XOR_OPERATOR, "^"),
                                     (OR_OPERATOR, "|"),
                                     (AND_OPERATOR, "&"),
                                     (EQUALITY_OPERATOR, "="),
                                     (PRINT_TOKEN, "PRINT"),
                                     (OPEN_PARENTHESES, "("),
                                     (IDENTIFIER_TOKEN_OPERATOR, "IDENTIFIER"),
                                     (CLOSE_PARENTHESES, ")")])
        self.VARS = {}

    def create_scanner(self, fp):
        self.SCANNER = plex.Scanner(self.LEXICON, fp)
        self.LA, self.TEXT = self.next_token()

    def next_token(self):
        a = self.SCANNER.read()
        return a

    def match(self,token):
        if self.LA == token:
            self.LA, self.TEXT = self.next_token()
        else:
            raise ParseError("self.LA not the same as token!")

    def parse(self,fp):
        self.create_scanner(fp)
        self.stmt_list()

    def stmt_list(self):
        if self.LA in ("IDENTIFIER", "PRINT"):
            self.stmt()
            self.stmt_list()
        elif self.LA == None:
            return
        else:
            raise ParseError("Expected ID, PRINT")

    def stmt(self):
        if self.LA == "IDENTIFIER":
            var = self.TEXT
            self.match("IDENTIFIER")
            self.match("=")
            value = self.expr()
            self.VARS[var] = value
        elif self.LA == "PRINT":
            self.match("PRINT")
            print(bin(self.expr()))
        else:
            raise ParseError("Expected ID, PRINT")

    def expr(self):
        if self.LA in ("(","IDENTIFIER", "NUMBER"):
            t = self.term()
            while self.LA == "^":
                self.xor()
                t ^= self.term()
            if self.LA in (")", "IDENTIFIER", "PRINT", None):
                return t
            raise ParseError("Expected something from expr's FOLLOW SET")
        else:
            raise ParseError("Expected (, ID, NUMBER")

    def term(self):
        if self.LA in ("(","IDENTIFIER", "NUMBER"):
            f = self.factor()
            while self.LA == "|":
                self.slash()
                f |= self.factor()
            if self.LA in ("^", "IDENTIFIER", ")", "PRINT", None):
                return f
            raise ParseError("Expected something from term's FOLLOW SET")
        else:
            raise ParseError("Expected (, ID, NUMBER")

    def factor(self):
        if self.LA in ("(","IDENTIFIER", "NUMBER"):
            a = self.atom()
            while self.LA == "&":
                self.amper()
                a &= self.factor()
            if self.LA in ("^", "|", "IDENTIFIER", ")", "PRINT", None):
                return a
            raise ParseError("Expected something from factor's FOLLOW SET")
        else:
            raise ParseError("Expected (, ID, NUMBER")

    def atom(self):
        if self.LA == "(":
            self.match("(")
            exp = self.expr()
            self.match(")")
            return exp
        elif self.LA == "IDENTIFIER":
            if self.VARS.get(self.TEXT) is not None:
                self.VALUE = self.VARS[self.TEXT]
            else:
                raise RunTimeError("IDENTIFIER has not initialized")
            self.match("IDENTIFIER")
            return self.VALUE
        elif self.LA == "NUMBER":
            self.VALUE = int(self.TEXT, 2)
            self.match("NUMBER")
            return self.VALUE
        else:
            raise ParseError("Expected (, ID, NUMBER")

    def xor(self):
        if self.LA == "^":
            self.match("^")
            return "^"
        else:
            raise ParseError("Expected ^")

    def slash(self):
        if self.LA == "|":
            self.match("|")
            return "|"
        else:
            raise ParseError("Expected /")

    def amper(self):
        if self.LA == "&":
            self.match("&")
            return "&"
        else:
            raise ParseError("Expected &")


parser = myParser()
with open("test.txt") as fp:
    parser.parse(fp)
