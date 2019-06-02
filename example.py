# coding=utf-8
from parsing import *

p = Parser()


@p.produce
def Main(e):
    """
    START -> E
    """
    return ("Main", e)


@p.produce
def Add(e1, _, e2):
    """
    E -> E + E
    """
    return ("Add", e1, e2)


@p.produce
def Mul(e1, _, e2):
    """
    E -> E * E
    """
    return ("Mul", e1, e2)


@p.produce
def Sub(e1, _, e2):
    """
    E -> E - E
    """
    return ("Sub", e1, e2)


@p.produce
def Div(e1, _, e2):
    """
    E -> E / E
    """
    return ("Div", e1, e2)


@p.produce
def Num(it):
    """
    E -> number
    """
    return ("Num", it)


p.setLevel("+", 4)
p.setLevel("-", 4)
p.setLevel("*", 5)
p.setLevel("/", 5)
# p.setAssoc('+',Left) default is Left
lex = Lexical([" ", "\n"], {})
lr1 = p.build(lex)
from pprint import pprint

pprint(lr1.action_table)
pprint(lr1.goto_table)
while 1:
    pprint(lr1.parse(input(">> ")))

# s-expression is abstract syntax tree
# string parsing to s-expression, and sexprcode interpreter,
# the machine run on sexprcode
