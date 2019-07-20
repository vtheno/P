# coding=utf-8
from collections import namedtuple
from log import print

Pair = namedtuple("Pair", ["tag", "hd", "tl"])

class Token(object):
    def __init__(self, tag, val, hd=None, tl=None):
        self.tag = tag
        self.val = val
        self.hd = hd
        self.tl = tl
    def __repr__(self):
        return "{}({})".format(self.tag, repr(self.val))
    def __len__(self):
        return len(self.val)

class tags(object):
    op = "op"
    tok = "tok"
    alnum = "alnum"
    number = "number"

class Self(object):

    def digit(inp):
        """
        inp: string
        if inp head element is "[0-9]"
        and inp tail element all is "[0-9]"
        """
        temp = ""
        if "0" <= inp[0] <= "9":
            while inp and ("0" <= inp[0] <= "9"):
                temp += inp[0]
                inp = inp[1:]
            if temp:
                # return Token(tags.number, temp), inp
                return temp, inp
    def num(inp):
        match_start = Self.digit(inp)
        if match_start:
            left, inp = match_start
            sym = ""
            if inp and inp[0] == ".":
                sym += inp[0]
                inp = inp[1:]
                match_end = Self.digit(inp)
                if match_end:
                    right, inp = match_end
                    return Token(tags.number, left + sym + right), inp
                else:
                    return Token(tags.number, left), sym + inp
            else:
                return Token(tags.number, left), inp

    def alpha(inp):
        """
        inp: string
        if inp head element is "[a-z|A-Z]"
        and inp tail element all is "[a-z|A-Z|0-9]"
        """
        temp = ""
        if "a" <= inp[0] <= "z" or "A" <= inp[0] <= "Z":

            while inp and (
                    "a" <= inp[0] <= "z" or "A" <= inp[0] <= "Z" or "0" <= inp[0] <= "9"
            ):
                temp += inp[0]
                inp = inp[1:]
            if temp:
                return Token(tags.alnum, temp), inp

    def ops(inp, spec):
        """
        inp: string
        spec: dict
        example:
            spec => {
                "=": ["=", ">"]
                "==": ["=", ">"]
            }
            # all element is ["==", "=>", "===", "==>" ]
        """
        if inp[0] in spec.keys():
            temp = "" + inp[0]
            inp = inp[1:]
            symbols = spec.get(temp)
            while inp and symbols and inp[0] in symbols:
                temp += inp[0]
                inp = inp[1:]
                symbols = spec.get(temp)
            # symbols is empty or result of sym non-single
            if temp and (not symbols or len(temp) > 1) :
                return Token(tags.op, temp), inp

    def parent(inp, spec_pairs):
        """
        inp: string
        spec: dict
        example:
            spec => [
                Pair(<ops spec>, <ops spec>),
                ...
        ]

        """
        for pair in spec_pairs:
            start = pair.hd
            end = pair.tl
            tag = pair.tag
            match_start = Self.ops(inp, start)
            if match_start:
                head, inp = match_start
                center = ""
                while inp and inp[0] not in end.keys():
                    center += inp[0]
                    inp = inp[1:]
                match_end = Self.ops(inp, end)
                if match_end:
                    tail, inp = match_end
                    return Token(tag, head.val + center + tail.val, head, tail) , inp


    def tok(inp):
        temp, inp  = inp[0], inp[1:]
        return Token(tags.tok, temp), inp

def lex(string, ops={}, parent=[]):
    cursor = 0
    line_number = 1
    column_number = 0
    inp = string
    self = Self
    ret = []
    push_ret = ret.append
    while cursor < len(string):
        match = self.parent(inp, parent)
        if match:
            val, inp = match
            push_ret(val)
            print("[parent] %s %s %s", repr(val), line_number, column_number)
            length = len(val)
            cursor = cursor + length
            column_number = column_number + length
            continue
        match = self.num(inp)
        if match:
            val, inp = match
            push_ret(val)
            print("[num] %s %s %s", repr(val), line_number, column_number)
            length = len(val)
            cursor = cursor + length
            column_number = column_number + length
            continue
        match = self.alpha(inp)
        if match:
            val, inp = match
            push_ret(val)
            print("[alpha] %s %s %s", repr(val), line_number, column_number)
            length = len(val)
            cursor = cursor + length
            column_number = column_number + length
            continue
        match = self.ops(inp, ops)
        if match:
            val, inp = match
            push_ret(val)
            print("[ops] %s %s %s", repr(val), line_number, column_number)
            length = len(val)
            cursor = cursor + length
            column_number = column_number + length
            continue
        match = self.tok(inp)
        if match:
            val, inp = match
            push_ret(val)
            print("[tok] %s %s %s", repr(val), line_number, column_number)
            if val.val == '\n':
                line_number = line_number + 1
                column_number = 0
            length = len(val)
            cursor = cursor + length
            column_number = column_number + length
            continue
    print( "[break]  %s %s", repr(inp), cursor )
    if not inp:
        return ret
    else:
        raise Exception("Lexical")

def skip_vals(inp: [Token], words: [str]) -> [Token]:
    return [i for i in inp if i.val not in words]
def skip_tags(inp: [Token], tags: [str]) -> [Token]:
    return [i for i in inp if i.tag not in tags]
def map_tag(inp: [Token], mapping: dict) -> [Token]:
    temp= list(inp)
    for cur in temp:
        cur.tag = mapping.get(cur.val, cur.tag)
    return temp

__all__ = [
    "Pair",
    "Token",
    "tags",
    "Self",
    "lex",
    "skip_vals", "skip_tags", "map_tag"
]
