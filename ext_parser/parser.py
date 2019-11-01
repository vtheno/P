class NonTerminal(object):
    def __init__(self, name: "string"):
        self.name = name
    def __eq__(self, obj):
        if isinstance(obj, self.__class__):
            return self.name == obj.name
        return False

class Terminal(object):
    def __init__(self, token: "token"):
        self.token = token
    def __eq__(self, obj):
        if isinstance(obj, self.__class__):
            # token.type == token.
            if self.token.type == obj.token.type:
                if self.token.type in ("symbol", "keyword"):
                    return self.token.value == obj.token.value
                return True
            return False
        return False

class StackPopError(Exception): pass

class Stack(object):
    # TODO shift reduce deduce error machine implement
    def __init__(self):
        self._s = []
        self._top = -1
    def push(self, value):
        self._s.append(value)
        self._top += 1
    def pop(self, n=1):
        while n:
            if self._s:    
                value = self._s.pop(0)
                self._top -= 1
                n -= 1
            else:
                raise StackPopError(f"{self._top}")
    def peek(self):
        return self._s[self._top]