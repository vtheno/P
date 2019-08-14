#!python
from parser.warp import Rule
from parser.warp import prod, sym
from parser.warp import LEFT, RIGHT
from parser.warp import non_terminal, terminal
from parser.warp import alnum, number

from parser.lex import skip_vals, map_tag
from parser.lex import lex

from parser.log import log, INFO
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
E_SEQ = sym("E_SEQ", non_terminal)
_comma = sym(",", terminal, "sep_comma")
E_SEQ_ITEM = sym("E_SEQ_ITEM", non_terminal)
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
    "fn": "key_fn",
    ",": "sep_comma",
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
def apply(e1, e2):
    """
    E -> E E
    """
    return {"apply": [e1, e2]}

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

@r(prod(E, [_lp, E_SEQ, _rp]))
def eseq(_1, seq, _2):
    """
    E -> ( E_SEQ )
    """
    return seq

@r(prod(E_SEQ, [E, _comma, E_SEQ_ITEM]))
def e_seq(e, _1, seq_item):
    """
    E_SEQ -> E , E_SEQ_ITEM
    """
    return {"E_SEQ": [e] + seq_item}

@r(prod(E_SEQ_ITEM, [E]))
def e_seq_item_1(e):
    """
    E_SEQ_ITEM -> E
    """
    return [e]
@r(prod(E_SEQ_ITEM, [E, _comma, E_SEQ_ITEM]))
def e_seq_item_2(e, _1, seq_item):
    """
    E_SEQ_ITEM -> E , E_SEQ_ITEM
    """
    return [e] + seq_item

# E_SEQ -> E, E_SEQ_ITEM
# E_SEQ_ITEM -> E
# E_SEQ_ITEM -> E, E_SEQ_ITEM
from pickle import dumps, loads
if False: # change BNF, modify False to True, else use cache
    from time import process_time as clock
    _clock = clock()
    lr1 = r.build()
    print( lr1, clock() - _clock )
    with open("cache", "wb") as file:
        file.write(dumps(lr1))
else:
    with open("cache", "rb") as file:
        data = file.read()
    lr1 = loads(data)

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
