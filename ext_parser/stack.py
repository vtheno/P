class StackError(Exception):
    pass

class Stack(object):
    def __init__(self, size=256 * 256 * 256):
        self.size = size
        self.items = [None] * size
        self.top = 0

    def push(self, val):
        if self.top < self.size:
            self.items[self.top] = val
            self.top += 1
            return self.top
        else:
            raise StackError(f"push {self.top} greate stack size {self.size}")

    def pop(self):
        if self.top > 0:
            self.top -= 1
            val = self.items[self.top]
            self.items[self.top] = None
            return val
        else:
            raise StackError(f"pop Empty")

    def peek(self):
        return self.items[self.top - 1]

    def __repr__(self):
        return f"{[i for i in self.items if i!=None]}"

class ValStack(object):
    def __init__(self):
        self.ctx = []

    def push(self, val):
        self.ctx += [val]

    def pop(self, n=1):
        out = list(reversed([self.ctx.pop() for _ in range(n)]))
        return out

    def __repr__(self):
        return f"{self.ctx}"
