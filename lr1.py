#coding=utf-8
from util import *
from lex import Lexical
from grammar import *

class ParseError(Exception): pass
class ConflictError(Exception): pass
class id(metaclass=Symbol): pass
class E(metaclass=Symbol): pass
class add(metaclass=Symbol): pass
class mul(metaclass=Symbol): pass
class Q(metaclass=Symbol): pass
class R(metaclass=Symbol): pass
class ELSE(metaclass=Symbol): pass
class IF(metaclass=Symbol): pass
class Compare(type):
    def __new__(cls,name,bases,attrs,**kws):
        attrs["__name__"] = name
        attrs["__repr__"] = lambda self: f"{self.__name__}"
        return type.__new__(cls,name,bases,attrs)()
class EQ(metaclass=Compare): pass
class LE(metaclass=Compare): pass
table = {
    id: 999,
    eof: 0,
    add: 1,
    mul: 2,
}
class GE(metaclass=Compare): pass
def compare(alpha,beta):
    a = table[alpha]
    b = table[beta]
    print( "compare =>", alpha,a,beta,b )
    _id = table[id]
    assert not (a == b == _id)
    if a > b:
        return GE
    elif a < b:
        return LE
    else:
        return EQ

class LR1(object):
    def __init__(self, 
                 lex: Lexical, 
                 translate: "str -> str",
                 rules: grammar,
                 level,
                 ):
        self.stack = Stack()
        self.lex = lex
        self.translate = translate
        self.R = rules
        self.Vt = self.R.Vt
        self.Vn = self.R.Vn
        self.V = self.R.V
        self.level = level
    def closure(self, I:[item]) -> [item]:
        I = I[:]
        changed = True
        while changed:
            changed = False
            for it in I:
                X = it.rest[0] if it.rest else []
                tail = it.rest[1:]
                tail = tail if tail else [eof]
                for b in self.R.first_point(tail + [it.lookahead,eof]):
                    if b!=bottom:
                        for name,body in self.R.R:
                            if X == name:
                                value = item(name,[],body,b)
                                if value not in I:
                                    I += [value]
                                    changed = True
        return I
    def goto(self,I:[item],X:"Vn"):
        return self.closure(
            [item(it.name,it.left + [it.rest[0]],it.rest[1:], it.lookahead) for it in I if it.rest and it.rest[0] == X]
        )
    def items(self):
        I0 = self.closure( [item(self.R.R[0][0],[],self.R.R[0][1],eof)] )
        self.C = [I0]
        self.targets = [{}]
        changed = True
        while changed:
            changed = False
            for i,I in enumerate(self.C):
                for X in self.V:
                    In = self.goto(I,X)
                    if In and In not in self.C:
                        self.C.append( In )
                        self.targets +=  [{}] 
                        self.targets[i][X] = self.C.index(In)
                        changed = True
                    if In in self.C:
                        self.targets[i][X] = self.C.index(In)
    def table(self):
        length_I = len(self.C)
        self.action_table = [{} for _ in range(length_I)]
        self.goto_table = [{} for _ in range(length_I)]
        self.locations = {}
        for i in range(length_I):
            for A in self.C[i]:
                if A.rest:
                    X = A.rest[0]
                    idx = self.targets[i][X]
                    shift = ('shift',idx)
                    # reduce-shift conflict problem at this
                    # shift-shift conflict problem at this
                    old_act,old_idx = self.action_table[i].get(A.lookahead,(None,None))
                    print( "conflict =>",X, (old_act,old_idx), shift)
                    if X in self.Vt:
                        self.action_table[i][X] = shift
                    else:
                        self.goto_table[i][X] = shift
                else:
                    R = (A.name,A.left)
                    idx = self.R.R.index(R)
                    reduce = ('reduce',idx)
                    old_act,old_idx = self.action_table[i].get(A.lookahead,(None,None))
                    if A.name == Start:
                        self.action_table[i][eof] = ('accept',0)
                    else:
                        if old_act == None:
                            self.action_table[i][A.lookahead] = reduce
                        elif old_act == 'shift':
                            # shift-reduce conflict
                            self.action_table[i][A.lookahead] = reduce
                        elif old_act == 'reduce':
                            # reduce-reduce conflict
                            print( 'reduce-reduce conflict =>',(old_act,old_idx),reduce)
                            if self.level[old_idx] > self.level[idx]:
                                self.action_table[i][A.lookahead] = (old_act,old_idx)
                            else:
                                self.action_table[i][A.lookahead] = reduce
                        else:
                            raise ConflictError
    def next (self,g : ... ):
        try:
            ret,token = self.translate(next(g))
        except StopIteration:
            ret,token = eof,None
        return ret,token
    def parse(self, inp):
        self.stack.push(0)
        g = self.lex.lex(inp)
        current,token = self.next(g)
        state = self.stack.peek
        while True:
            #print( current, token, self.stack )
            print( self.stack ) 
            act,In_of_n = self.action_table[state()][current]
            print( "=>", act,In_of_n )
            if act == 'shift':
                self.stack.push(token)
                self.stack.push(In_of_n)
                current,token = self.next(g)
            elif act == 'reduce':
                name,body = self.R.R[In_of_n]
                drops = [self.stack.pop() for _ in body*2]
                n = state()
                self.stack.push(name)
                new_act,new_In_of_n = self.goto_table[n][name]
                self.stack.push(new_In_of_n)
                #print( drops, new_act, new_In_of_n )
            elif act == 'accept':
                name,body = self.R.R[0]
                drops = [self.stack.pop() for _ in body*2]
                return 

rules = [
    (Start,[E]),
    (E,[E,add,E]),
    (E,[E,mul,E]),
    (E,[id]),
]
level = [
    None,
    1,
    2,
    999,
]
vt = [id,add,mul]
vn = [Start,E]
R = grammar(rules,vt,vn)
print( R.first_set )
lex = Lexical([" ","\n"],{})
def translate(s):
    if s == '+':
        return (add,s)
    elif s == '*':
        return (mul,s)
    elif s == 'if':
        return (IF,s)
    elif s == 'else':
        return (ELSE,s)
    return (id,s)
lr = LR1(lex,translate,R,level)

from pprint import pprint
lr.items()
pprint( lr.C )
print( "----------------------------------------" )
pprint( lr.targets )
print( "----------------------------------------" )
lr.table()
print( "----------------------------------------" )
pprint( lr.action_table )
print( "----------------------------------------" )
pprint( lr.goto_table )
print( "----------------------------------------" )
print( lr.parse("""
a + b * c + d
""") )
"""
# todo 
# 1. how reslove shift-reduce(SR) or reduce-reduce(RR) conflicts problem
"""
