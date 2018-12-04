#coding=utf-8
from util import *
from lex import Lexical
"""
E -> E op E | id
op -> + | *
--------
E -> E + E 
   | E * E
   | id
   | if E then E else E
"""
class eof(metaclass=Symbol): pass
class ident(metaclass=Symbol): pass
class add(metaclass=Symbol): pass
class mul(metaclass=Symbol): pass
table = {
    ident: 999,
    eof: 0,
    add: 1,
    mul: 2,
}
func = {
    ident: lambda i: {'id':i},
    add: lambda a,_,b: {'add':[a,b]},
    mul: lambda a,_,b: {'mul':[a,b]},
}
class Compare(type):
    def __new__(cls,name,bases,attrs,**kws):
        attrs["__name__"] = name
        attrs["__repr__"] = lambda self: f"{self.__name__}"
        return type.__new__(cls,name,bases,attrs)()
class EQ(metaclass=Compare): pass
class LE(metaclass=Compare): pass
class GE(metaclass=Compare): pass
def compare(alpha,beta):
    a = table[alpha]
    b = table[beta]
    print( "compare =>", alpha,a,beta,b )
    _ident = table[ident]
    assert not (a == b == _ident)
    if a > b:
        return GE
    elif a < b:
        return LE
    else:
        return EQ
class Parsing(object):
    def __init__(self,lex: Lexical,translate : "str -> str"):
        self.lex = lex
        self.translate = translate
    def next(self,inp : "Generator"):
        try:
            ret,val = self.translate(next(inp))
        except StopIteration:
            ret,val = eof,None
        return ret,val
    def parse(self,inp : str):
        self.stack = Stack ()
        self.stack.push(eof)
        self.values = Stack()
        inp = self.lex.lex(inp)
        alpha,cur_val = self.next(inp)
        beta = self.stack.peek
        while True:
            comp_flag = compare(alpha,beta())
            if alpha == eof and beta() == eof:
                return self.values.pop()
            elif comp_flag == GE or comp_flag == EQ:
                self.stack.push( alpha )
                self.values.push( cur_val )
                alpha,cur_val = self.next(inp)
            elif comp_flag == LE:
                while True:
                    current = self.stack.pop()
                    flag = compare(current,beta())
                    if flag == GE or flag == EQ:
                        val = func[current]
                        count = val.__code__.co_argcount 
                        args = list(reversed([self.values.pop() for _ in range(count)]))
                        print( "=>", current,args, self.values )
                        self.values.push ( val(*args) )
                        break
            else:
                pass
        
skips = [" ","\n","\t"]
spectab = {
    "=":["="],
    "-":[">"],
}
lex = Lexical(skips,spectab)
def translate(s: str) -> str:
    if s == "+":
        return (add,s)
    elif s == "*":
        return (mul,s)
    return (ident,s)
parse = Parsing(lex,translate).parse

print( parse("a + b * c + d * e * f") )
"""
单纯的 Operator Precedence Parsing 无法解决一部分问题
  对 lr0 部分 Shift Reduce 冲突部分进行标记
  根据 Precedence 进行解决冲突
"""
