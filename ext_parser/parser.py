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
