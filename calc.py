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
_if = sym("if", terminal, "key_if")
_then = sym('then', terminal, "key_then")
_else = sym("else", terminal, "key_else")
_lp = sym("(", terminal, "op_lp")
_rp = sym(")", terminal, "op_rp")
op_tags = {
    "+": "op_add",
    "-": "op_sub",
    "*": "op_mul",
    "/": "op_div",
    "if": "key_if",
    "then": "key_then",
    "else": "key_else",
    "(": "op_lp",
    ")": "op_rp",
}
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
    return {"num": it}

@r(prod(E, [alnum]))
def alnum(it):
    """
    E -> alnum
    """
    return {"alnum": it}

@r(prod(E, [E, E]))
def app(e1, e2):
    """
    E -> E E
    """
    return {"app": [e1, e2]}

@r(prod(E, [_if, E, _then, E, _else, E]))
def cond(_1, e1, _2, e2, _3, e3):
    """
    E -> if E then E else E
    """
    return {"cond": [e1, e2, e3]}

@r(prod(E, [_lp, E, _rp]))
def parent(_1, e, _2):
    """
    E -> ( E )
    """
    return {"parent": [e]}

lr1 = r.build()
print( lr1 )
def lexical(inp: str):
    lex_inp = skip_vals(lex(inp), [" ", "\n", "\t", "\r"])
    lex_inp = map_tag(lex_inp, op_tags)
    return lex_inp

def repl():
    while 1:
        inp = input("=> ")
        if inp == ":q":
            print("Goodbye!")
            break
        elif inp == ":h":
            print( r.__class__.__doc__ )
        else:
            try:
                inp = lexical(inp)
                out = lr1.parse(inp)
                print( inp )
                print( out )
            except Exception as e:
                print( "[ERROR]", e )



if __name__ == "__main__":
    repl()
