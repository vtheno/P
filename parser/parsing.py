from collections import namedtuple
from parser.stack import Stack, ValStack
_print = print
from parser.log import print
from parser.lex import tags, Token

sym = namedtuple("sym", ['name', 'typ', 'tag'], defaults=(None, None, None))
# sym.__repr__ = lambda self: repr(self.name) # debug

non_terminal = 0
terminal = 1

prod = namedtuple("prod", ["left", "right"])

item = namedtuple("item", ["name", "left", "rest", "lookahead"])
item.__repr__ = (
    lambda self: f"{self.name} = {' '.join([repr(i) for i in self.left])} @ {' '.join([repr(i) for i in self.rest])} ;; {self.lookahead}"
)

def all_V(prods):
    lefts  = [prod.left for prod in prods]
    rights = [r for prod in prods for r in  prod.right]
    return list(set(lefts + rights))

def all_vt(sets):
    return list(i for i in sets if i.typ == terminal)

def all_vn(sets):
    return list(i for i in sets if i.typ == non_terminal)

eof = sym("\0", terminal)
alnum = sym("alnum", terminal, tags.alnum)
number = sym("number", terminal, tags.number)

class Grammar(object):
    def __init__(self, g, vt, vn):
        # v = vt + vn
        # vt is terminal
        # vn is non_terminal
        self.R = g # [prod]
        self.S = self.R[0].left
        self.vt = vt
        self.vn = vn
        self.V = self.vt + self.vn
        self.first_set = {}
        self.nullable_set = {}
        self.init_set()
        self.compute_nullable()
        self.compute_first()
        print("[nullable_set] %s", self.nullable_set)
        print("[first_set] %s", self.first_set)

    def init_set(self):
        self.nullable_set[eof] = True
        self.first_set[eof] = [eof]
        for x in self.V:
            self.nullable_set[x] = False
            if x in self.vt:
                self.first_set[x] = [x]
            else:
                self.first_set[x] = []

    def sum(self, lst):
        print("[sum] %s", lst)
        ret = []
        for i in lst:
            value = [x for x in i if x not in ret]
            if value:
                ret += value
        return ret

    def null_point(self, lst):
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
            for x in self.vn:
                for name, body in self.R:
                    if name == x:
                        value = self.null_point(body)
                        if value and value != self.nullable_set[name]:
                            self.nullable_set[name] = value
                            changed = True

    def first_point(self, lst):
        i, l = 0, len(lst)
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
            for x in self.vn:
                print("[x] %s", x)
                value = self.sum([self.first_point(y) for X, y in self.R if X == x])
                if value and value != self.first_set[x]:
                    value = [i for i in value if i not in self.first_set[x]]
                    if value:
                        self.first_set[x] += value
                        changed = True

GE = 0
LE = 1
EQ = 2

LEFT = 0
RIGHT = 1

class LR1(object):
    def __init__(self,
                 grammar,
                 op_level,
                 op_assoc,
                 func_maps,
    ):
        self.G = grammar
        self.V = self.G.V
        self.Vt = self.G.vt
        self.Vn = self.G.vn
        self.Start = self.G.S
        self.op_level = op_level
        self.op_assoc = op_assoc
        self.func_maps = func_maps

        self.C = []
        self.action_table = []
        self.goto_table = []

        self.stack = []
        self.values = []
        self.cache_keys = []
        self.cache_values = []
        self.cache_length = 0

        self.items()
        self.table()

    def thread_closure(self, I, X, b, changeds):
        for name, body in self.G.R:
            if X == name:
                value = item(name, [], body, b)
                if value not in I:
                    I.append(value)
                    changeds.append(True)
                    # changed = True


    def closure(self, I: [item]) -> [item]:
        I = list(I)
        changed = True
        while changed:
            changed = False
            for it in I:
                X = it.rest[0] if it.rest else []
                tail = it.rest[1:]
                tail = tail if tail else [eof]
                for name, body in self.G.R:
                    if X == name:
                        for b in self.G.first_point(tail + [it.lookahead, eof]):
                            value = item(name, [], body, b)
                            if value not in I:
                                I.append(value)
                                changed = True
        return I

    def goto(self, I: [item], X: terminal + non_terminal):
        key = [
            item(it.name, it.left + [it.rest[0]], it.rest[1:], it.lookahead)
            for it in I
            if it.rest and it.rest[0] == X
        ]
        for idx in range(self.cache_length):
            i, x = self.cache_keys[idx]
            if i == I and x == X:
                return self.cache_values[idx]
        else:
            value = self.closure(key)
            self.cache_keys.append((I, X))
            self.cache_values.append(value)
            self.cache_length += 1
            return value

    def items(self):
        I0 = self.closure([item(self.G.R[0][0], [], self.G.R[0][1], eof)])
        self.C = [I0]
        changed = True
        while changed:
            changed = False
            for I in self.C:
                for X in self.V:
                    In = self.goto(I, X)
                    if In and In not in self.C:
                        self.C.append(In)
                        changed = True
    def compare(self, alpha, beta):
        print("[compare 1] %s %s", alpha, beta)
        a = self.op_level.get(alpha, None)
        b = self.op_level.get(beta, None)
        print("[compare 2] %s %s", a, b)
        if a == None or b == None:
            return None
        _id = self.op_level[alnum]
        assert not (a == b == _id)
        if a > b:
            return GE
        elif a < b:
            return LE
        elif a == b:
            return EQ

    def table(self):
        length_I = len(self.C)
        self.action_table = [{} for _ in range(length_I)]
        self.goto_table = [{} for _ in range(length_I)]
        for i in range(length_I):
            Ci = self.C[i]
            for it in Ci:
                if it.rest:
                    X = it.rest[0]
                    lookahead = it.lookahead
                    if X in self.Vt:
                        Cj = self.goto(Ci, X)
                        if Cj:
                            j = self.C.index(Cj)
                            shift = ("shift", j)
                            # shift-shift or reduce-shift or accept-shift
                            self.action_table[i][X] = shift
            for it in Ci:
                if it.rest == []:
                    if it.name == self.Start:
                        self.action_table[i][eof] = ("accept", 0)
                    else:
                        rule = (it.name, it.left + it.rest)
                        rule_idx = self.G.R.index(rule)
                        reduce = ("reduce", rule_idx)
                        before = self.action_table[i].get(it.lookahead)
                        lookahead = it.lookahead
                        if before:
                            if before[0] == "shift":  # shift-reduce conflict
                                X = [x for x in it.left if x in self.Vt]
                                # print( ">>>", X )
                                if X == []:  # grammar not have Vt
                                    self.action_table[i][it.lookahead] = reduce
                                    continue
                                else:
                                    X = X[-1]
                                cmp_flag = self.compare(lookahead, X)
                                # print( i, "|",it,"|", lookahead,cmp_flag,X,before,reduce )
                                if cmp_flag == EQ:
                                    # default associative is LEFT
                                    X_assoc = self.op_assoc.get(X, LEFT)
                                    lookahead_assoc = self.op_assoc.get(lookahead, LEFT)
                                    if X_assoc != lookahead_assoc:
                                        raise AssociativeError(
                                            "left- and right-associative operators of equal op_level"
                                        )
                                    if X == lookahead:
                                        if lookahead_assoc == LEFT:
                                            self.action_table[i][lookahead] = reduce
                                        else:
                                            # lookahead_assoc == Right
                                            self.action_table[i][lookahead] = before
                                    else:  # X not is lookahead
                                        if lookahead_assoc == LEFT:
                                            self.action_table[i][lookahead] = reduce
                                        else:
                                            # lookahead_assoc == Right
                                            self.action_table[i][lookahead] = before
                                elif cmp_flag == GE:
                                    self.action_table[i][lookahead] = before
                                elif cmp_flag == LE:
                                    self.action_table[i][lookahead] = reduce
                                else:  # default lookahead cmp_flag X is GE
                                    # 无优先级声明则默认为高优先级
                                    self.action_table[i][lookahead] = before
                            else:
                                raise ConflictError(
                                    f" => NoSupport resloving Reduce-Reduce !!"
                                )
                        else:
                            self.action_table[i][it.lookahead] = reduce
            for A in self.Vn:
                Cj = self.goto(Ci, A)
                if Cj:
                    j = self.C.index(Cj)
                    self.goto_table[i][A] = ("shift", j)

    def mapping(self, token: Token, V: [sym]) -> (item, Token):
        env = {s.name:s for s in V if not s.tag}
        tag = {s.tag:s for s in V if s.tag}
        # print("[env] %s %s %s", env, tag, token)
        ret = env.get(token.val, None) # op, keywords
        if not ret: # if token.val is non-terminal
            ret = tag.get(token.tag, None)
        return ret, token.val

    def next(self, g: iter):
        try:
            ret, token = self.mapping(next(g), self.V)
        except StopIteration:
            ret, token = eof, None
        return ret, token

    def parse(self, inp: [str]):
        self.stack = Stack()
        self.values = ValStack()
        self.stack.push(0)
        g = iter(inp)
        current, token = self.next(g)
        print( "[current] %s %s", current, token )
        self.values.push(token)
        state = self.stack.peek
        while 1:
            # print( current, token, self.stack )
            # print( "stack:",self.stack )
            # print( "value:",self.values )
            try:
                act, In_of_n = self.action_table[state()][current]
            except KeyError:
                raise Exception(f"Ran into a `{token}` where it wasn't expected")
            # print( "=>", act,In_of_n )
            if not (token is None) and act == "shift":
                self.values.push(token)
            if act == "shift":
                self.stack.push(token)
                self.stack.push(In_of_n)
                current, token = self.next(g)

            elif act == "reduce":
                name, body = self.G.R[In_of_n]
                drops = [self.stack.pop() for _ in body * 2]
                n = state()
                self.stack.push(name)
                new_act, new_In_of_n = self.goto_table[n][name]
                self.stack.push(new_In_of_n)
                # value ast

                func = self.func_maps[In_of_n]
                # print( "[body] %s", body )
                # count = func.__code__.co_argcount
                count = len(body)
                args = self.values.pop(count)

                self.values.push(func(*args))

            elif act == "accept":
                name, body = self.G.R[0]
                drops = [self.stack.pop() for _ in body * 2]
                func = self.func_maps[0]
                args = self.values.pop()
                return func(*args)
            else:
                raise Exception(f"Ran into a `{token}` where it wasn't expected")


__all__ = [
    "sym", "prod",
    "non_terminal", "terminal",
    "all_V", "all_vt", "all_vn",
    "item",
    "eof", "alnum", "number",
    "Grammar", "LR1",
    "GE", "LE", "EQ",
    "LEFT", "RIGHT"
]
