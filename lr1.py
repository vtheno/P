#coding=utf-8
from util import *
from lex import Lexical
from grammar import *

class ParseError(Exception): pass
class ConflictError(Exception): pass
class Compare(type):
    def __new__(cls,name,bases,attrs,**kws):
        attrs["__name__"] = name
        attrs["__repr__"] = lambda self: f"{self.__name__}"
        return type.__new__(cls,name,bases,attrs)()
class EQ(metaclass=Compare): pass
class LE(metaclass=Compare): pass
class GE(metaclass=Compare): pass
class Associative(type):
    def __new__(cls,name,bases,attrs,**kws):
        attrs["__name__"] = name
        attrs["__repr__"] = lambda self: f"{self.__name__}"
        return type.__new__(cls,name,bases,attrs)()
class Left(metaclass=Associative): pass
class Right(metaclass=Associative): pass

class id(metaclass=Symbol): pass
class E(metaclass=Symbol): pass
class add(metaclass=Symbol): pass
class mul(metaclass=Symbol): pass
class sub(metaclass=Symbol): pass
class div(metaclass=Symbol): pass
class ELSE(metaclass=Symbol): pass
class IF(metaclass=Symbol): pass

table = {
    id: 999,
    eof: 0,
    add: 1,
    sub: 1,
    mul: 3,
    div: 3,
}
assocs = {
    add: Left,
    sub: Left,
    mul: Left,
    div: Left,
}
def compare(alpha,beta):
    a = table[alpha]
    b = table[beta]
    # print( "compare =>", alpha,a,beta,b )
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
                 ):
        self.stack = Stack()
        self.values = ASTStack()
        self.lex = lex
        self.translate = translate
        self.R = rules
        self.Vt = self.R.Vt
        self.Vn = self.R.Vn
        self.V = self.R.V
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
        # self.targets = [{}]
        changed = True
        while changed:
            changed = False
            for i,I in enumerate(self.C):
                for X in self.V:
                    In = self.goto(I,X)
                    if In and In not in self.C:
                        self.C.append( In )
                        # self.targets +=  [{}] 
                        # self.targets[i][X] = self.C.index(In)
                        changed = True
                    #if In in self.C:
                    #    self.targets[i][X] = self.C.index(In)
    def table(self):
        length_I = len(self.C)
        self.action_table = [{} for _ in range(length_I)]
        self.goto_table = [{} for _ in range(length_I)]
        for i in range(length_I):
            Ci = self.C[i]
            for it in Ci:
                if it.rest:
                    X = it.rest[0]
                    lookahead = it.lookahead
                    if X in self.Vt:
                        Cj = self.goto(Ci,X)
                        if Cj:
                            j = self.C.index(Cj)
                            shift = ('shift',j)
                            self.action_table[i][X] = shift
            for it in Ci:
                if it.rest == []:
                    if it.name == Start:
                        self.action_table[i][eof] = ('accept',0)
                    else:
                        rule = (it.name,it.left + it.rest)
                        rule_idx = self.R.R.index(rule)
                        reduce = ('reduce',rule_idx)
                        before = self.action_table[i].get(it.lookahead)
                        lookahead = it.lookahead
                        if before:
                            if before[0] == 'shift':
                                X = [x for x in it.left if x in self.Vt][-1]
                                cmp_flag = compare(lookahead, X) 
                                print( i, "|",it,"|", X,cmp_flag,lookahead,before,reduce )
                                if cmp_flag == EQ:
                                    assert assocs[X] == assocs[lookahead]
                                    if X == lookahead:
                                        if assocs[lookahead] == Left:
                                            self.action_table[i][lookahead] = reduce
                                        else:
                                            self.action_table[i][lookahead] = before
                                    else:
                                        if assocs[lookahead] == Left:
                                            self.action_table[i][lookahead] = reduce
                                        else:
                                            self.action_table[i][lookahead] = before
                                elif cmp_flag == GE:
                                    self.action_table[i][lookahead] = before
                                else:
                                    self.action_table[i][lookahead] = reduce
                            else:
                                raise ConflictError(f" => NoSupport resloving Reduce-Reduce !!")
                        else:
                            self.action_table[i][it.lookahead] = reduce
            for A in self.Vn:
                Cj = self.goto(Ci,A)
                if Cj:
                    j = self.C.index(Cj)
                    self.goto_table[i][A] = ('shift',j)
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
        self.values.push( token )
        state = self.stack.peek
        while True:
            #print( current, token, self.stack )
            print( "stack:",self.stack )
            print( "value:",self.values )
            act,In_of_n = self.action_table[state()][current]
            print( "=>", act,In_of_n )
            if not (token is None) and act == 'shift':
                self.values.push(token)
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
                # value ast 
                print( "reduce --- start" )
                print( "pop before:", self.values )
                func = func_maps[In_of_n]
                count = func.__code__.co_argcount
                args = self.values.pop(count)
                print( "args:", args )
                print( "pop after:", self.values )
                self.values.push( func(*args) )
                print( "push after:", self.values )
                print( "reduce --- done" )
                #print( drops, new_act, new_In_of_n )
            elif act == 'accept':
                name,body = self.R.R[0]
                drops = [self.stack.pop() for _ in body*2]
                func = func_maps[0]
                args = self.values.pop()
                return func(*args)
            else:
                raise ParseError("I don't know what's happen, i'm sorry...")
rules = [
    (Start,[E]),
    (E,[E,add,E]),
    (E,[E,mul,E]),
    (E,[E,sub,E]),
    (E,[E,div,E]),
    (E,[id]),
]
vt = [id,add,mul,sub,div]
vn = [Start,E]
func_maps = [
    lambda e: e,
    lambda e1,_,e2: {"+":[e1,e2]},
    lambda e1,_,e2: {"*":[e1,e2]},
    lambda e1,_,e2: {"-":[e1,e2]},
    lambda e1,_,e2: {"/":[e1,e2]},
    lambda it: {"id":[it]},
]
R = grammar(rules,vt,vn)
print( R.first_set )
lex = Lexical([" ","\n"],{})
def translate(s):
    if s == '+':
        return (add,s)
    elif s == '*':
        return (mul,s)
    elif s == '-':
        return (sub,s)
    elif s == '/':
        return (div,s)
    elif s == 'if':
        return (IF,s)
    elif s == 'else':
        return (ELSE,s)
    return (id,s)
lr = LR1(lex,translate,R)

from pprint import pprint
lr.items()
# pprint( lr.C )
print( "----------------------------------------" )
# pprint( lr.targets )
print( "----------------------------------------" )
lr.table()
print( "----------------------------------------" )
def format(table):
    def get_rows(row):
        reject = ' ' * len("('reject',1)")
        ID = row.get(id,reject)
        ADD = row.get(add,reject)
        SUB = row.get(sub,reject)
        MUL = row.get(mul,reject)
        DIV = row.get(div,reject)
        EOF = row.get(eof,reject)
        return ID,ADD,SUB,MUL,DIV,EOF
    def row_format(ID,ADD,SUB,MUL,DIV,EOF):
        return f"{ID}\t{ADD}\t{SUB}\t{MUL}\t{DIV}\t{EOF}"
    print( "  ","id\t\tadd\t\tsub\t\tmul\t\tdiv\t\teof" )
    for i,row in enumerate(table):
        print( f"{i}",row_format(*get_rows(row)) )
format( lr.action_table )
print( "----------------------------------------" )
# pprint( lr.goto_table )
print( "----------------------------------------" )
pprint( lr.parse("""
a + b * b - c * c / 2
""") )
"""
# todo 
# 1. how reslove shift-reduce(SR) or reduce-reduce(RR) conflicts problem
"""
