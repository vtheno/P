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
sub = sym("-", terminal, "op_sub")
mul = sym("*", terminal, "op_mul")
div = sym("/", terminal, "op_div")


@r(prod(S, [E]))
def s(expr):
    """
    S -> E
    """
    return expr

@r(prod(E, [E, add, E]), {add: 5}, {})
def add(e1, op, e2):
    """
    E -> E + E
    """
    return {op: [e1, e2]}

@r(prod(E, [E, sub, E]), {sub: 5}, {})
def sub(e1, op, e2):
    """
    E -> E - E
    """
    return {op: [e1, e2]}

@r(prod(E, [E, mul, E]), {mul: 6}, {})
def mul(e1, op, e2):
    """
    E -> E * E
    """
    return {op: [e1, e2]}

@r(prod(E, [E, div, E]), {div: 6}, {})
def div(e1, op, e2):
    """
    E -> E / E
    """
    return {op: [e1, e2]}

@r(prod(E, [number]))
def num(it):
    """
    E -> number
    """
    return {'num': it}

@r(prod(E, [alnum]))
def alnum(it):
    """
    E -> alnum
    """
    return {'alnum': it}

lr1 = r.build()
print( lr1 )
def lexical(inp: str):
    lex_inp = skip_vals(lex(inp), [" ", "\n", "\t", "\r"])
    op_tags = {
        "+": "op_add",
        "-": "op_sub",
        "*": "op_mul",
        "/": "op_div",
    }
    lex_inp = map_tag(lex_inp, op_tags)
    return lex_inp

while 1:
    inp = input("=> ")
    if inp != ":q":
        inp = lexical(inp)
        out = lr1.parse(inp)
        print( inp )
        print( out )
    else:
        print("Goodbye!")
        break
