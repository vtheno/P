#coding=utf-8
from util import *
from lex import Lexical
from grammar import *

class ParseError(Exception): pass
class ConflictError(Exception): pass
class CompareError(Exception): pass
class AssociativeError(Exception): pass
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

class LR1(object):
    def __init__(self, 
                 lex: Lexical, 
                 translate: "str -> (Symbol * str)",
                 rules: grammar,
                 precedence: {Symbol: int},
                 assocs: {Symbol: Associative},
                 func_maps: "(args -> ast) list",
                 ):
        self.lex = lex
        self.translate = translate
        self.R = rules
        self.Vt = self.R.Vt
        self.Vn = self.R.Vn
        self.V = self.R.V
        self.Start = self.R.R[0][0]
        self.precedence = precedence
        self.assocs = assocs
        self.func_maps = func_maps
    def closure(self, I:[item]) -> [item]:
        I = list(I)
        changed = True
        while changed:
            changed = False
            for it in I:
                X = it.rest[0] if it.rest else []
                tail = it.rest[1:]
                tail = tail if tail else [eof]
                for b in self.R.first_point(tail + [it.lookahead,eof]):
                #for b in self.R.first_point(tail + [it.lookahead]):
                    #if b!=bottom:
                    for name,body in self.R.R:
                        if X == name:
                            value = item(name,[],body,b)
                            if value not in I:
                                I += [value]
                                changed = True
        return I
    def goto(self,I:[item],X:"Vn"):
        return self.closure(
            item(it.name,it.left + [it.rest[0]],it.rest[1:], it.lookahead) for it in I if it.rest and it.rest[0] == X
        )
    def items(self):
        I0 = self.closure( [item(self.R.R[0][0],[],self.R.R[0][1],eof)] )
        self.C = [I0]
        # self.targets = [{}]
        changed = True
        while changed:
            changed = False
            for I in self.C:
                for X in self.V:
                    In = self.goto(I,X)
                    if In and In not in self.C:
                        self.C.append( In )
                        # self.targets +=  [{}] 
                        # self.targets[i][X] = self.C.index(In)
                        changed = True
                    #if In in self.C:
                    #    self.targets[i][X] = self.C.index(In)
    def compare(self,alpha,beta):
            a = self.precedence.get(alpha,None)
            b = self.precedence.get(beta,None)
            if a == None or b == None:
                return None
            # print( "compare =>", alpha,a,beta,b )
            _id = self.precedence[id]
            assert not (a == b == _id)
            if a > b:
                return GE
            elif a < b:
                return LE
            elif a == b:
                return EQ
            else:
                raise CompareError
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
                    if it.name == self.Start:
                        self.action_table[i][eof] = ('accept',0)
                    else:
                        rule = (it.name,it.left + it.rest)
                        rule_idx = self.R.R.index(rule)
                        reduce = ('reduce',rule_idx)
                        before = self.action_table[i].get(it.lookahead)
                        lookahead = it.lookahead
                        if before:
                            if before[0] == 'shift': # shift-reduce conflict
                                X = [x for x in it.left if x in self.Vt]
                                # print( ">>>", X )
                                if X == []: # grammar not have Vt
                                    self.action_table[i][it.lookahead] = reduce
                                    continue
                                else:
                                    X = X[-1]
                                cmp_flag = self.compare(lookahead, X) 
                                # print( i, "|",it,"|", X,cmp_flag,lookahead,before,reduce )
                                if cmp_flag == EQ:
                                    # default associative is Left
                                    X_assoc = self.assocs.get(X,Left)
                                    lookahead_assoc = self.assocs.get(lookahead,Left)
                                    if X_assoc != lookahead_assoc:
                                        raise AssociativeError("left- and right-associative operators of equal precedence")
                                    if X == lookahead:
                                        if lookahead_assoc == Left:
                                            self.action_table[i][lookahead] = reduce
                                        else:
                                            # lookahead_assoc == Right
                                            self.action_table[i][lookahead] = before
                                    else:
                                        if lookahead_assoc == Left:
                                            self.action_table[i][lookahead] = reduce
                                        else:
                                            # lookahead_assoc == Right
                                            self.action_table[i][lookahead] = before
                                elif cmp_flag == GE:
                                    self.action_table[i][lookahead] = before
                                elif cmp_flag == LE:
                                    self.action_table[i][lookahead] = reduce
                                else:# default lookahead cmp_flag X is GE
                                    self.action_table[i][lookahead] = before
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
        self.stack = Stack()
        self.values = ASTStack()
        self.stack.push(0)
        g = self.lex.lex(inp)
        current,token = self.next(g)
        self.values.push( token )
        state = self.stack.peek
        while True:
            #print( current, token, self.stack )
            #print( "stack:",self.stack )
            #print( "value:",self.values )
            act,In_of_n = self.action_table[state()][current]
            #print( "=>", act,In_of_n )
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
                #print( "reduce --- start" )
                #print( "pop before:", self.values )
                func = self.func_maps[In_of_n]
                count = func.__code__.co_argcount
                args = self.values.pop(count)
                #print( "args:", args )
                #print( "pop after:", self.values )
                self.values.push( func(*args) )
                #print( "push after:", self.values )
                #print( "reduce --- done" )
                #print( drops, new_act, new_In_of_n )
            elif act == 'accept':
                name,body = self.R.R[0]
                drops = [self.stack.pop() for _ in body*2]
                func = self.func_maps[0]
                args = self.values.pop()
                return func(*args)
            else:
                raise ParseError("I don't know what's happen, i'm sorry...")
class E(metaclass=Symbol): pass
class add(metaclass=Symbol): pass
class mul(metaclass=Symbol): pass
class sub(metaclass=Symbol): pass
class div(metaclass=Symbol): pass

class IF(metaclass=Symbol): pass
class THEN(metaclass=Symbol): pass
class ELSE(metaclass=Symbol): pass
class LET(metaclass=Symbol): pass
class ASSGIN(metaclass=Symbol): pass
class IN(metaclass=Symbol): pass

table = {
    id: 999,
    eof: 0,
    add: 4,
    sub: 4,
    mul: 5,
    div: 5,
#    IF: 1,
#    THEN: 1,
#    ELSE: 1,
}
assocs = {
    add: Left,
    sub: Left,
    mul: Left,
    div: Left,
}
rules = [
    (Start,[E]),
    (E,[E,add,E]),
    (E,[E,mul,E]),
    (E,[E,sub,E]),
    (E,[E,div,E]),
    (E,[IF,E,THEN,E,ELSE,E]),
    (E,[LET,id,ASSGIN,E,IN,E]),
    (E,[E,E]),
    (E,[id]),
]
vt = [id,add,mul] + [sub,div] + [IF,THEN,ELSE] + [LET,ASSGIN,IN]
vn = [Start,E]
func_maps = [
    lambda e: e,
    lambda e1,_,e2: {"+":[e1,e2]},
    lambda e1,_,e2: {"*":[e1,e2]},
    lambda e1,_,e2: {"-":[e1,e2]},
    lambda e1,_,e2: {"/":[e1,e2]},
    lambda _i,e1,_t,e2,_e,e3: {"if":[e1,e2,e3]},
    lambda _l,v,_a,e1,_i,e2:{"let":[(v,e1),e2]},
    lambda e1,e2: {"app":[e1,e2]},
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
    elif s == "then":
        return (THEN,s)
    elif s == 'else':
        return (ELSE,s)
    elif s == 'let':
        return (LET,s)
    elif s == '=':
        return (ASSGIN,s)
    elif s == 'in':
        return (IN,s)
    return (id,s)
lr = LR1(lex,translate,R,table,assocs, func_maps)
from time import clock
from pprint import pprint
t1 = clock()
lr.items()
print( clock() - t1 )
# pprint( lr.C )
print( "----------------------------------------" )
# pprint( lr.targets )
print( "----------------------------------------" )
t1 = clock()
lr.table()
print( clock() - t1 )
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
# format( lr.action_table )
print( "----------------------------------------" )
# pprint( lr.goto_table )
print( "----------------------------------------" )
#pprint( lr.parse("""
#a + b * b - c * c / 2
#""") )
print( 'time clock' )
t1 = clock()
pprint( lr.parse("""
if let a = 2 
   in a * 1 + 3 / 2 
then a + b * b - c * c / 2
else f arg
""") )
print( clock() - t1 )
"""
# todo 
# 1. how reslove shift-reduce(SR) or reduce-reduce(RR) conflicts problem
"""
