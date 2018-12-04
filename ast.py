#coding=utf-8
from tool import data
class Type(metaclass=data): pass
class Pair(Type,init="init",show="show"):
    def init(self,typ1, typ2):
        self.typ1 = typ1
        self.typ2 = typ2
    def show(self):
        return f"{{Pair: ({self.typ1!r}, {self.typ2!r})}}"
class Atom(Type,init="init",show="show"): pass
