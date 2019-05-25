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
            self.match("IDENTIFIER")
            self.match("=")
            self.expr()
        elif self.LA == "PRINT":
            self.match("PRINT")
            self.expr()
        else:
            raise ParseError("Expected ID, PRINT")

    def expr(self):
        if self.LA in ("(","IDENTIFIER", "NUMBER",")"):
            self.term()
            self.term_tail()
        else:
            raise ParseError("Didnt get what i was expecting!")

    def term_tail(self):
        if self.LA == "^":
            self.xor()
            self.term()
            self.term_tail()
        elif self.LA in ("IDENTIFIER", "PRINT", ")", None):
            return
        else:
            raise ParseError("Expected ^")

    def term(self):
        if self.LA in ("(","IDENTIFIER", "NUMBER"):
            self.factor()
            self.factor_tail()
        else:
            raise ParseError("Expected (, ID, NUMBER")

    def factor_tail(self):
        if self.LA == "|":
            self.slash()
            self.factor()
            self.factor_tail()
            return op, eval(f"{f}t[0]{t[1]}")
        elif self.LA in (")", "^", "IDENTIFIER", "PRINT", None):
            return
        else:
            raise ParseError("Expected |")

    def factor(self):
        if self.LA in ("(","IDENTIFIER", "NUMBER"):
            self.atom()
            self.atom_tail()
        else:
            raise ParseError("Expected (, ID, NUMBER")

    def atom_tail(self):
        if self.LA == "&":
            self.amper()
            self.atom()
            self.atom_tail()
        elif self.LA in ("|", "^", "IDENTIFIER", "PRINT", ")", None):
            return
        else:
            raise ParseError("Expected &")

    def atom(self):
        if self.LA == "(":
            self.match("(")
            self.expr()
            self.match(")")
        elif self.LA == "IDENTIFIER":
            self.match("IDENTIFIER")
        elif self.LA == "NUMBER":
            self.match("NUMBER")
        else:
            raise ParseError("Expected (, ID, NUMBER")

    def xor(self):
        if self.LA == "^":
            self.match("^")
        else:
            raise ParseError("Expected ^")

    def slash(self):
        if self.LA == "|":
            self.match("|")
        else:
            raise ParseError("Expected /")

    def amper(self):
        if self.LA == "&":
            self.match("&")
        else:
            raise ParseError("Expected &")


parser = myParser()
with open("test.txt") as fp:
    parser.parse(fp)
