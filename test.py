#coding=utf-8
from lr1 import *
E = mkSym("E")
add = mkSym("+")
mul = mkSym("*")

table = {
    ident: 999,
    number: 999,
    EOF: 0,
    add: 4,
    mul: 5,
}
assocs = {
    add: Left,
    mul: Left,
}
rules = [
    (START,[E]),
    (E,[E,add,E]),
    (E,[E,mul,E]),
    (E,[ident]),
]
vt = [add,mul] + [ident]
vn = [START,E]
R = grammar(rules,vt,vn)
func_maps = [
    lambda e: {"main":e},
    lambda e1,_,e2: {"add":[e1,e2]},
    lambda e1,_,e2: {"mul":[e1,e2]},
    lambda id: {"id":id},
]
lex = Lexical([" ","\n"],{})
def translate(s):
    global vn,vt
    V = dict([(i.__name__,i) for i in vn + vt if i not in [ident,number]])
    ret = V.get(s,None)
    if ret is None:
        ret = number if s.isdigit() else ident
    # print( ret, s )
    return ret,s
lr1 = LR1(lex,translate,R,table,assocs, func_maps)
from pprint import pprint
pprint( lr1.action_table )
pprint( lr1.goto_table )
print( lr1.parse("a + b * c + d") )
