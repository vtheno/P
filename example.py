#coding=utf-8
from lr1 import *
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
"""
无优先级声明则默认为高优先级
"""
table = {
    ident: 999,
    number: 999,
    EOF: 0,
    add: 4,
    sub: 4,
    mul: 5,
    div: 5,
}
assocs = {
    add: Left,
    sub: Left,
    mul: Left,
    div: Left,
}
rules = [
    (START,[E]),
    (E,[E,add,E]),
    (E,[E,mul,E]),
    (E,[E,sub,E]),
    (E,[E,div,E]),
    (E,[IF,E,THEN,E,ELSE,E]),
    (E,[LET,IDENT,ASSGIN,E,IN,E]),
    (E,[E,E]),
    (E,[ident]),
    (E,[number]),
]
"""
START -> Expr
Expr -> Expr + Expr
Expr -> Expr * Expr
Expr -> Expr - Expr
Expr -> Expr / Expr
Expr -> if Expr then Expr else Expr
Expr -> let ident = Expr in Expr
Expr -> Expr Expr
Expr -> ident
Expr -> number
"""
vt = [ident,number] + [add,mul] + [sub,div] + [IF,THEN,ELSE] + [LET,ASSGIN,IN]
vn = [START,E]
func_maps = [
    lambda e: e,
    lambda e1,_,e2: {"+":[e1,e2]},
    lambda e1,_,e2: {"*":[e1,e2]},
    lambda e1,_,e2: {"-":[e1,e2]},
    lambda e1,_,e2: {"/":[e1,e2]},
    lambda _i,e1,_t,e2,_e,e3: {"if":[e1,e2,e3]},
    lambda _l,v,_a,e1,_i,e2:{"let":[(v,e1),e2]},
    lambda e1,e2: {"app":[e1,e2]},
    lambda it: {"ident":[it]},
    lambda it: {"number":[it]},
]
R = grammar(rules,vt,vn)
# print( R.first_set )
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
    elif s.isdigit():
        return (number, s)
    return (ident,s)
from time import clock
from pprint import pprint
t1 = clock()
lr = LR1(lex,translate,R,table,assocs, func_maps)
print( "items =>",clock() - t1 )
print( "----------------------------------------" )
t1 = clock()
ast = lr.parse("""
if let a = 2 
   in a * 1 + 3 / 2 
then a + b * b - c * c / 2
else 2 + f arg
""")
print( "parse =>", clock() - t1 )
pprint( ast )
