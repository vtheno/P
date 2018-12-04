#coding=utf-8
from util import Symbol
class bottom(metaclass=Symbol): pass
class eof(metaclass=Symbol): pass
class Start(metaclass=Symbol): pass

from collections import namedtuple

item = namedtuple('item',['name','left','rest','lookahead'])
item.__repr__ = lambda self:f"{self.name} = {' '.join([repr(i) for i in self.left])} @ {' '.join([repr(i) for i in self.rest])} ;; {self.lookahead}"

class grammar(object):
    def __init__(self,
                 g: [(Symbol,[Symbol])],
                 vt: [Symbol],
                 vn: [Symbol], ):
        self.R = g
        self.S = self.R[0][0]
        self.Vt = vt
        self.Vn = vn
        self.V = self.Vt + self.Vn
        self.first_set = {}
        self.follow_set = {}
        self.nullable_set = {}
        self.init_set()
        self.compute_nullable()
        self.compute_first()
    def init_set(self):
        self.nullable_set[bottom] = True
        self.nullable_set[eof] = True
        self.first_set[bottom] = [bottom]
        self.first_set[eof] = [eof]
        for x in self.V:
            self.nullable_set[x] = False
            if x in self.Vt:
                self.first_set[x] = [x]
            else:
                self.first_set[x] = []
                self.follow_set[x] = []
        self.follow_set[self.S] = [eof]
    def sum(self, lst):
        ret = [ ]
        for i in lst:
            value = [x for x in i if x not in ret]
            if value:
                ret += value
        return ret
    def null_point(self,lst):
        flag = True if self.nullable_set[lst[0]] else False
        for i in lst[1:]:
            if flag:
                flag = self.nullable_set[i]
            else:
                break
        return flag
    def compute_nullable(self):
        changed = True
        while changed:
            changed = False
            for x in self.Vn:
                for name,body in self.R:
                    if name == x:
                        value = self.null_point(body)
                        if value and value != self.nullable_set[name]:
                            self.nullable_set[name] = value
                            changed = True
    def first_point(self,lst):
        i,l = 0,len(lst)
        current = lst[i]
        first_x = self.first_set[current][:]
        changed = True
        while changed and i < l - 1 and self.nullable_set[current]:
            changed = False
            i += 1
            current = lst[i]
            value = [i for i in self.first_set[current] if i not in first_x]
            if value:
                first_x += value
                changed = True
        return first_x
    def compute_first(self):
        changed = True
        while changed:
            changed = False
            for x in self.Vn:
                value = self.sum([self.first_point(y) for X,y in self.R if X == x])
                if value and value != self.first_set[x]:
                    value = [i for i in value if i not in self.first_set[x]]
                    if value:
                        self.first_set[x] += value
                        changed = True
