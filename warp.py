from parsing import prod, sym
from parsing import eof, number, alnum
from parsing import terminal, non_terminal
from parsing import all_V, all_vt, all_vn
from parsing import LR1, Grammar
from parsing import LEFT, RIGHT

__all__ = [
    "LEFT", "RIGHT",
    "terminal", "non_terminal",
    "number", "alnum",
    "prod", "sym",
    "Rule"
]
class Rule(object):
    def __init__(self):
        self.R = [ ]
        self.push = self.R.append
        self.op_assoc = {}
        self.op_level = {
            alnum: 999,
            number: 999,
            eof: -1,
        }
        self.func_maps = []
        self.push_fn = self.func_maps.append
        self.__class__.__doc__ = ""

    def __call__(self, p: prod, op_level: dict={}, op_assoc: dict={}):
        self.push(p)
        self.op_level.update(op_level)
        self.op_assoc.update(op_assoc)
        def _(fn):
            self.push_fn(fn)
            self.__class__.__doc__ += fn.__doc__.strip("\n")
            return fn
        return _

    def build(self):
        V = all_V(self.R)
        vt = all_vt(V)
        vn = all_vn(V)
        g =  Grammar(self.R, vt, vn)
        lr1 = LR1(g, self.op_level, self.op_assoc, self.func_maps)
        return lr1
