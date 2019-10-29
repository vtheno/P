from log import print
from collections import namedtuple
class One(object): 
    def __repr__(self):
        return "<One>"

one = One()
__all__ = ["Token", "Lexical", "LexicalError"]

Token = namedtuple("Token", ["type", "value"])
class LexicalError(Exception): pass

class _Lexical(object):
    def lex_ident(self, inp: "string", *, spec: "char list") -> "token * string":
        token = ""
        if inp:
            x, *xs = inp
            if x in spec:
                token += x
                while xs:
                    x, *xs = xs
                    if x in spec:
                        token += x
                    else:
                        xs = [x] + xs
                        break
                return Token(type="ident", value=token), xs
            return None
        return None

    def lex_spec(self, chunk: "string -> token", inp: "string", spec: "{str : str list}") -> "token * string":
        token = ""
        if inp:
            x, *xs = inp
            token += x
            if token in spec.keys():
                symbols = spec.get(token, [])
                while symbols and xs:
                    x, *xs = xs
                    if x in symbols:
                        token += x
                        symbols = spec.get(token, [])
                    else:
                        xs = [x] + xs
                        break
                # print( f"#### { one in spec.get(token, []) }" )
                if len(token) == 1:
                    if one in spec.get(token, []):
                        return chunk(token), xs
                    return None, [token] + xs
                else:
                    return chunk(token), xs
            return None
        return None
    
    def lex_skip(self, inp, *, spec):
        return self.lex_spec(lambda token: Token("skip", token), inp, spec)
    def lex_symbol(self, inp, *, spec):
        return self.lex_spec(lambda token: Token("symbol", token), inp, spec)
    def lex_keyword(self, inp, *, spec):
        return self.lex_spec(lambda token: Token("keyword", token), inp, spec)
    
    def lex(self, inp, *, ident_spec, skip_spec, symbol_spec, keyword_spec):
        c = 0
        old_inp = inp
        while inp:
            match = self.lex_skip(inp, spec=skip_spec)
            if match:
                print(match)
                token, inp = match
                c += len(token.value)
                yield from token
                continue

            match = self.lex_symbol(inp, spec=symbol_spec)
            if match:
                print(match)    
                token, inp = match
                c += len(token.value)
                yield from token
                continue

            match = self.lex_keyword(inp, spec=keyword_spec)
            if match:
                print(match)    
                token, inp = match
                if token:
                    c += len(token.value)    
                    yield from token
                    continue

            match = self.lex_ident(inp, spec=ident_spec)
            if match:
                print(match)
                token, inp  = match
                c += len(token.value)
                yield from token
                continue
                
            lineno = old_inp[:c].count('\n')
            offset = old_inp[:c].rfind("\n")
            column = c - offset
            raise LexicalError(f"at Line {lineno}, Column {column}")

class Lexical(object):
    def __init__(self):
        self.ident_spec = list(map(chr, range(ord("A"), ord("Z") + 1))) + \
                            list(map(chr, range(ord("a"), ord("z") + 1))) + ["_"]
        self.skip_spec = {}
        self.symbol_spec = {}
        self.keyword_spec = {}
        self._lex = _Lexical().lex

    def register_spec(self, symbol, symbol_spec):
        if symbol:
            prefix = ""
            if len(symbol) == 1:
                if symbol not in symbol_spec.keys():
                    symbol_spec[symbol] = [one]
            while len(symbol) > 1:
                x, *xs = symbol
                prefix += x
                symbol = ''.join(xs)
                if len(xs) == 1:
                    if prefix not in symbol_spec.keys():
                        symbol_spec[prefix] = [symbol]
                    else:
                        if symbol not in symbol_spec[prefix]:
                            symbol_spec[prefix].append(symbol)
                        else:
                            raise ValueError(f"register({prefix + symbol !r}, ...) exists")
                else:
                    sym = symbol[0]
                    if prefix not in symbol_spec.keys():
                        symbol_spec[prefix] = [sym]
                    else:
                        if sym not in symbol_spec[prefix]:
                            symbol_spec[prefix].append(sym)
            # print("%r %r %r", prefix, symbol, symbol_spec)
        else:
            raise ValueError(f"register({symbol!r}, ...)")
    def register_skip(self, skip: "string"):
        self.register_spec(skip, self.skip_spec)
    def register_symbol(self, symbol: "string"):
        self.register_spec(symbol, self.symbol_spec)
    def register_keyword(self, keyword: "string"):
        self.register_spec(keyword, self.keyword_spec)
    def lex(self, inp):
        return self._lex(inp, skip_spec=self.skip_spec, symbol_spec=self.symbol_spec, ident_spec=self.ident_spec, keyword_spec=self.keyword_spec)

llex = Lexical()
llex.register_symbol("=")
llex.register_symbol("=>")
llex.register_symbol("==>")
llex.register_symbol("==<")
print(llex.symbol_spec)
llex.register_keyword("let")
llex.register_keyword("in")
print(llex.keyword_spec)
llex.register_skip("\n")
llex.register_skip(" ")
print(llex.skip_spec)
print(llex.ident_spec)
ret = llex.lex("""
let a => l in b
abcdef \t
""")
print(list(ret))