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
        self.Start = self.R.S
        self.precedence = precedence
        self.assocs = assocs
        self.func_maps = func_maps
        self.C = []
        self.action_table = []
        self.goto_table = []
        self.stack = []
        self.values = []
        self.cache_keys = []
        self.cache_values = []
        self.cache_length = 0
        self.items()
        self.table()
    def closure(self, I:[item]) -> [item]:
        I = list(I)
        changed = True
        while changed:
            changed = False
            for it in I:
                X = it.rest[0] if it.rest else []
                tail = it.rest[1:]
                tail = tail if tail else [EOF]
                for b in self.R.first_point(tail + [it.lookahead,EOF]):
                #for b in self.R.first_point(tail + [it.lookahead]):
                    #if b!=bottom:
                    for name,body in self.R.R:
                        if X == name:
                            value = item(name,[],body,b)
                            if value not in I:
                                I.append( value )
                                changed = True
        return I
    def goto(self,I:[item],X:"V"):
        # old version 
        # return self.closure( item(it.name,it.left + [it.rest[0]],it.rest[1:], it.lookahead) for it in I if it.rest and it.rest[0] == X )
        key = [item(it.name,it.left + [it.rest[0]],it.rest[1:], it.lookahead) for it in I if it.rest and it.rest[0] == X]
        for idx in range(self.cache_length):
            i,x = self.cache_keys[idx]
            if i == I and x == X:
                return self.cache_values[idx]
        else:
            self.cache_keys.append((I,X))
            self.cache_length += 1
            value = self.closure( key )
            self.cache_values.append( value )
            return value
    def items(self):
        I0 = self.closure( [item(self.R.R[0][0],[],self.R.R[0][1],EOF)] )
        self.C = [I0]
        changed = True
        while changed:
            changed = False
            for I in self.C:
                for X in self.V:
                    In = self.goto(I,X)
                    if In and In not in self.C:
                        self.C.append( In )
                        changed = True
    def compare(self,alpha,beta):
        a = self.precedence.get(alpha,None)
        b = self.precedence.get(beta,None)
        if a == None or b == None:
            return None
        _id = self.precedence[ident]
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
                            # shift-shift or reduce-shift or accept-shift
                            self.action_table[i][X] = shift
            for it in Ci:
                if it.rest == []:
                    if it.name == self.Start:
                        self.action_table[i][EOF] = ('accept',0)
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
                                # print( i, "|",it,"|", lookahead,cmp_flag,X,before,reduce )
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
                                    else: # X not is lookahead 
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
                                    # 无优先级声明则默认为高优先级
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
            ret,token = EOF,None
        return ret,token
    def parse(self, inp):
        self.stack = Stack()
        self.values = ASTStack()
        self.stack.push(0)
        g = self.lex.lex(inp)
        current,token = self.next(g)
        self.values.push( token )
        state = self.stack.peek
        while 1:
            # print( current, token, self.stack )
            # print( "stack:",self.stack )
            # print( "value:",self.values )
            try:
                act,In_of_n = self.action_table[state()][current]
            except KeyError:
                raise ParseError(f"Ran into a ``{token}`` where it wasn't expected")
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
                raise ParseError(f"Ran into a ``{token}`` where it wasn't expected")

__all__ = ["Left","Right","Associative",
           "ident","number","START","EOF",
           "Symbol","mkSym","ParseError",
           "LR1","Lexical","grammar"]
