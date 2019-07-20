#!python
from lex import *
from parsing import prod, sym, eof, number, alnum, terminal, non_terminal, all_V, all_vt, all_vn, LR1, Grammar


inp = """
S -> E;  -- program start by E
E -> E {+, op_add, 5, left} E;
E -> E {*, op_mul, 6, right} E;
E -> number;
E -> alnum;
"""

ops = {
    "-": [">"], # two op
}
parent = [
    Pair("comment",
        { "-": ["-"], },
        { "\n": [],   }),
    Pair("terminal",
        { "{": [], },
        { "}": [], })
]
lex_inp = lex(inp, ops=ops, parent=parent)
lex_inp = skip_tags(lex_inp, ["comment"])
lex_inp = skip_vals(lex_inp, [" ","\n","\t"])
print( list(lex_inp) )
def process(name, tag, level, assoc):
    return sym(name, terminal, tag)
prods = []
p = []
def build_map(val):
    e = {
        "alnum": alnum,
        "number": number
    }
    return e.get(val, None)
for i in lex_inp:
    if i.tag == "terminal":
        r = process(*[x.strip() for x in i.val[1:-1].split(",")])
        p += [r]
    elif i.val == ";":
        prods += [p]
        p = []
    else:
        r = build_map(i.val)
        if not r:
            if i.val != "->":
                r = sym(i.val, non_terminal)
        p += [r]
from pprint import pprint
ps = []
for p in prods:
    offset = p.index(None)
    ps += [prod(p[:offset], p[offset+1:])]
for p in ps:
    print(p)

# add new support with Parser
