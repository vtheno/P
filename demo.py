#!python
from parsing import *
p = Parser()

"""
START -> EXPR
EXPR -> ATOM
EXPR -> LIST
LIST -> ( EXPR LISTITEM )
LISTITEM -> EXPR LISTITEM
LISTITEM -> EXPR
ATOM -> number
"""

@p.produce
def main(e):
    """
    START -> LIST
    """
    return {"start": [e]}

@p.produce
def exprFromAtom(e):
    """
    EXPR -> ATOM
    """
    return {"expr": [e]}
@p.produce
def exprFromList(e):
    """
    EXPR -> LIST
    """
    return {"expr": [e]}

@p.produce
def list(_lp, e, item, _rp):
    """
    LIST -> ( EXPR LISTITEM )
    """
    print
    return {"list": [e] + item}
@p.produce
def listItem1(e):
    """
    LISTITEM -> EXPR
    """
    return [e]

@p.produce
def listItem2(e, tail):
    """
    LISTITEM -> EXPR LISTITEM
    """
    return [e] + tail

@p.produce
def atomFromNum(it):
    """
    ATOM -> ident
    """
    return {"atom": [it]}

@p.produce
def atomFromNum(it):
    """
    ATOM -> number
    """
    return {"atom": [it]}

lex = Lexical([" ", "\n"], {})
lr1 = p.build(lex)
from pprint import pprint

while 1:
    pprint(lr1.parse(input(">> ")))
