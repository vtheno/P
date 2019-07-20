#!python
from warp import Rule
from warp import prod, sym
from warp import LEFT, RIGHT
from warp import non_terminal, terminal
from warp import alnum, number

from lex import skip_vals, map_tag
from lex import lex

from log import log, INFO
log.setLevel(INFO)

r = Rule()
S = sym("S", non_terminal)
E = sym("E", non_terminal)
add = sym("+", terminal, "op_add")
mul = sym("*", terminal, "op_mul")
@r(prod(S, [E]))
def s(expr):
    return expr

@r(prod(E, [E, add, E]), {add: 5}, {})
def add(e1, op, e2):
    return {op: [e1, e2]}

@r(prod(E, [E, mul, E]), {mul: 6}, {})
def mul(e1, op, e2):
    return {op: [e1, e2]}

@r(prod(E, [number]))
def num(it):
    return {'num': it}

lr1 = r.build()
print( lr1 )
inp = input("=> ")
lex_inp = skip_vals(lex(inp), [" ", "\n", "\t", "\r"])
op_tags = {
    "+": "op_add",
    "*": "op_mul",
}
lex_inp = map_tag(lex_inp, op_tags)
print( lex_inp )
print( lr1.parse(lex_inp) )
