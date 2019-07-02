#!python
from parsing import prod, sym, eof, number, alnum, terminal, non_terminal, all_sets, all_vt, all_vn, LR1, Grammar
from lex import lex, Token, skips, map_tag
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
sets = all_sets(R)
vt = all_vt(sets)
vn = all_vn(sets)
from pprint import pprint
print("[V]", sets )
print("[vt]", vt )
print("[vn]", vn )
# TEST

g = Grammar(R, vt, vn)
print( g )
level = {
    sym("+", terminal, "op_add"): 5,
    sym("*", terminal, "op_mul"): 6,
    alnum: 999,
    number: 999,
    eof: 0,
}
assocs = {
}
def mapping(token: Token, V: [sym]):
    # print( "[mapping]",  list(map(type, V)) )
    # env = {s.name:s for s in V if s.name not in ["alnum", "number"] }
    env = {s.name:s for s in V if not s.tag}
    tag = {s.tag:s for s in V if s.tag}
    # print("[mapping][env]", env)
    ret = env.get(token.val, None) # op, keywords
    print("[mapping][ret]", ret)
    if not ret:
        print( "[mapping]", token.val.isdigit() )
        ret = tag.get(token.tag, None)
        # ret = number if token.val.isdigit() else alnum
    print( "[mapping]", ret, token )
    return ret, token.val
func_maps = [
    lambda e: e,
    lambda e1, _, e2: {_:[e1,e2]},
    lambda e1, _, e2: {_:[e1,e2]},
    lambda n: {"num": n}
]
lr1 = LR1(g, level, assocs, func_maps, mapping)
print( lr1 )
print("-" * 50)
pprint( lr1.C )
print("-" * 50)
for idx in range(lr1.cache_length):
    I, X = lr1.cache_keys[idx]
    V = lr1.cache_values[idx]
    if V:
        print(lr1.C.index(I), X, lr1.C.index(V))
print("-" * 50)
pprint( lr1.action_table )
print("-" * 50)
pprint( lr1.goto_table )
print("-" * 50)
# rmap

inp = """
123 * 456 + 678
"""

lex_inp = skips(lex(inp), [" ", "\n"])
# skips
op_tags = {
    "+": "op_add",
    "*": "op_mul",
}
lex_inp = map_tag(lex_inp, op_tags)
print( "[lex_inp]", lex_inp )
pprint( lr1.parse( lex_inp ) )
