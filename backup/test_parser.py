#!python
from parsing import prod, sym, eof, number, alnum, terminal, non_terminal, all_V, all_vt, all_vn, LR1, Grammar
from lex import lex, Token, skip_vals, map_tag
_print = print
from log import log, print, INFO
log.setLevel(INFO)
"""
# BNF terminal is a type of token
# non-terminal is a function of terminal
S -> E
E -> E + E
E -> E * E
E -> number
E -> alnum
"""
# TEST
p0 = prod(sym("S", non_terminal), [sym("E", non_terminal)])
p1 = prod(sym("E", non_terminal), [sym("E", non_terminal), sym("+", terminal, "op_add"), sym("E", non_terminal)])
p2 = prod(sym("E", non_terminal), [sym("E", non_terminal), sym("*", terminal, "op_mul"), sym("E", non_terminal)])
p3 = prod(sym("E", non_terminal), [number])
p4 = prod(sym("E", non_terminal), [alnum])
R = [p0, p1, p2, p3, p4]
sets = all_V(R)
vt = all_vt(sets)
vn = all_vn(sets)
from pprint import pprint
print("[V] %s", sets )
print("[vt] %s", vt )
print("[vn] %s", vn )
# TEST

g = Grammar(R, vt, vn)
print("[g] %s", g )
print("[V] %s", g.V )
level = {
    sym("+", terminal, "op_add"): 5,
    sym("*", terminal, "op_mul"): 6,
    alnum: 999,
    number: 999,
    eof: 0,
}
assocs = {
}
func_maps = [
    lambda e: e,
    lambda e1, _, e2: {_:[e1,e2]},
    lambda e1, _, e2: {_:[e1,e2]},
    lambda n: {"num": n}
]
lr1 = LR1(g, level, assocs, func_maps)
print( lr1 )
_print("-" * 50)
# pprint( lr1.C )
_print("-" * 50)
for idx in range(lr1.cache_length):
    I, X = lr1.cache_keys[idx]
    V = lr1.cache_values[idx]
    if V:
        print("%s %s %s", lr1.C.index(I), X, lr1.C.index(V))
_print("-" * 50)
# pprint( lr1.action_table )
_print("-" * 50)
# pprint( lr1.goto_table )
_print("-" * 50)
# rmap

inp = """
1.23 * 4.56 + 678
"""

lex_inp = skip_vals(lex(inp), [" ", "\n"])
# skips
op_tags = {
    "+": "op_add",
    "*": "op_mul",
}
print("[lex_inp] %s", lex_inp)
lex_inp = map_tag(lex_inp, op_tags)
print( "[lex_inp] %s", lex_inp )
pprint( lr1.parse( lex_inp ) )
