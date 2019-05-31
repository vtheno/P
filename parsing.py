# coding=utf-8
from lr1 import *


class GrammarParsingError(Exception):
    def __init__(self, msg: str):
        self.msg = msg

    def __repr__(self):
        return f"{self.__name__}: {self.msg}"


class Parser(object):
    __doc__ = """
    buildin keywords: [START, EOF, ident, number]
    """

    def __init__(self):
        self.Vt = []
        self.Vn = []
        self.rules = []
        self.func_maps = []
        self.table = {ident: 9999, number: 9999, EOF: 0}
        self.assocs = {}

    def get(self, name: str, collections):
        if name == "ident":
            return ident
        elif name == "number":
            return number
        elif name == "START":
            return START
        elif name == "EOF":
            return EOF
        for i in collections:
            if i.__name__ == name:
                return i
        return mkSym(name)

    def parse(self, inp: str) -> [Symbol]:
        tmp = [i.strip("\n") for i in inp.split(" ") if i]
        # print( tmp )
        if tmp[1] == "->":
            name = tmp[0]
            obj = self.get(name, self.Vn)
            if name.isupper():
                if name not in [i.__name__ for i in self.Vn]:
                    self.Vn.append(obj)
            else:
                raise GrammarParsingError(f"{name} require upper")
            rest = tmp[2:]
            rs = []
            for name in rest:
                o = self.get(name, self.Vn + self.Vt)
                rs += [o]
                if name.isupper():
                    if name not in [i.__name__ for i in self.Vn]:
                        self.Vn.append(o)
                else:
                    if name not in [i.__name__ for i in self.Vt]:
                        self.Vt.append(o)
            self.rules.append((obj, rs))
        else:
            raise GrammarParsingError(inp)

    def produce(self, func):
        doc = func.__doc__.strip("\n")
        self.parse(doc)
        self.func_maps.append(func)
        return func

    def translate(self, s: str):
        V = dict(
            [(i.__name__, i) for i in self.Vn + self.Vt if i not in [ident, number]]
        )
        ret = V.get(s, None)
        if ret is None:
            ret = number if s.isdigit() else ident
        # print( ret, s )
        return ret, s

    def setLevel(self, name: str, level: int):
        V = dict(
            [(i.__name__, i) for i in self.Vn + self.Vt if i not in [ident, number]]
        )
        ret = V.get(name, None)
        if ret and 0 < level < 9999:
            self.table[ret] = level
        else:
            raise ParseError(f"{name!r} is not used") if ret is None else ParseError(
                f"0 < {level!r} < 9999"
            )

    def setAssoc(self, name: str, assoc: Associative):
        V = dict(
            [(i.__name__, i) for i in self.Vn + self.Vt if i not in [ident, number]]
        )
        ret = V.get(name, None)
        # print( name, ret, assoc,isinstance(type(assoc),Associative) )
        if ret and isinstance(type(assoc), Associative):
            self.assocs[ret] = assoc
        else:
            raise ParseError(f"{name!r} is not used") if ret is None else ParseError(
                f"{assoc!r} choice [Left | Right]"
            )

    def build(self, lex: Lexical):
        return LR1(
            lex,
            self.translate,
            grammar(self.rules, self.Vt, self.Vn),
            self.table,
            self.assocs,
            self.func_maps,
        )


__all__ = ["Parser", "Left", "Right", "Lexical"]
# todo add a dump action_table and goto_table to file and load it from file
