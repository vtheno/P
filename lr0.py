#coding=utf-8
from util import *
from lex import Lexical

from collections import namedtuple

item = namedtuple('item',['name','left','rest'])
item.__repr__ = lambda self:f"{self.name} = {' '.join([repr(i) for i in self.left])} @ {' '.join([repr(i) for i in self.rest])}"
class ParseError(Exception): pass

class Start(metaclass=Symbol): pass
class eof(metaclass=Symbol): pass
class id(metaclass=Symbol): pass


class E(metaclass=Symbol): pass
class add(metaclass=Symbol): pass
class mul(metaclass=Symbol): pass
class lp(metaclass=Symbol): pass
class rp(metaclass=Symbol): pass

class LR0(object):
    def __init__(self, 
                 lex: Lexical, 
                 translate: "str -> str",
                 Vt,
                 Vn,
                 rules,
                 level, ):
        self.stack = Stack()
        self.lex = lex
        self.translate = translate
        self.Vt = Vt
        self.Vn = Vn
        self.V = self.Vt + self.Vn
        self.rules = rules
        self.level = level
    def closure(self, I:[item]) -> [item]:
        I = I[:]
        changed = True
        while changed:
            changed = False
            for it in I:
                if it.rest and (it.rest[0] in self.Vn):
                    nextVn = it.rest[0]
                    for name,tail in self.rules:
                        if name == nextVn:
                            value = item(name,[],tail)
                            if value not in I:
                                changed = True
                                I.append(value)
        return I
    def goto(self,I:[item],X:"Vn"):
        return self.closure(
            [item(it.name,it.left + [it.rest[0]],it.rest[1:]) for it in I if it.rest and it.rest[0] == X]
        )
    def items(self):
        I0 = self.closure( [item(self.rules[0][0],[],self.rules[0][1])] )
        #print( I0 )
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
                        self.targets[i][X] = i + 1
                        changed = True
                    if In in self.C:
                        self.targets[i][X] = self.C.index(In)
        return self.targets
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
                    if X in self.Vt:
                        reduce = False#self.action_table[i].get(X,None)
                        if reduce:
                            print ( i, X, reduce )
                            if self.locations.get(i,None) is None:
                                self.locations[i] = []
                            self.locations[i] += [{X:dict([reduce,shift])}]
                            self.action_table[i][X] = None#('shift',idx)
                        else:
                            self.action_table[i][X] = shift
                    else:
                        self.goto_table[i][X] = shift
                else:
                    R = (A.name,A.left)
                    idx = self.rules.index(R)
                    if A.name == Start:
                        self.action_table[i][eof] = ('accept',0)
                    else:
                        for x in self.Vt + [eof]:
                            self.action_table[i][x] = ('reduce',idx)
        for i,env in self.locations.items():
            print( '=>',i , env )
            for e in env:
                for _,v in e.items():
                    for k in self.Vt + [eof]:
                        if k == mul:
                            self.action_table[i][k] = ('shift',v['shift'])
                        else:
                            self.action_table[i][k] = ('reduce',v['reduce'])
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
                name,body = self.rules[In_of_n]
                drops = [self.stack.pop() for _ in body*2]
                n = state()
                self.stack.push(name)
                new_act,new_In_of_n = self.goto_table[n][name]
                self.stack.push(new_In_of_n)
                print( drops, new_act, new_In_of_n )
            elif act == 'accept':
                name,body = self.rules[0]
                drops = [self.stack.pop() for _ in body*2]
                return 
rules = [
    (Start,[E]),
    (E,[E,mul,E]),
    (E,[E,add,E]),
    (E,[id]),
]
level = [
    None,
    2,
    1,
    999
]
vt = [add,mul,id]
vn = [E]
lex = Lexical([" ","\n"],{})
def translate(s):
    if s == '+':
        return (add,s)
    elif s == '*':
        return (mul,s)
    return (id,s)
lr = LR0(lex,translate,vt,vn,rules,level)
from pprint import pprint
# print( lr.items() )
lr.items()
pprint( lr.C )
lr.table()
pprint( lr.action_table )
pprint( lr.goto_table )
lr.parse("a b c") 
