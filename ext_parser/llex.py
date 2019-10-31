from log import print
class One(object): 
    def __repr__(self):
        return "<One>"

one = One()
__all__ = ["Token", "Lexical", "LexicalError"]
class Token(object):
    def __init__(self, type, value, lineno, column):
        self.type = type
        self.value = value
        self.lineno = lineno
        self.column = column
    def __repr__(self):
        return f"{self.type}({self.value!r}, lineno={self.lineno}, column={self.column})"

class LexicalError(Exception): pass

class _Lexical(object):
    def lex_seq(self, chunk: "string -> token", inp: "string", spec_head: "char list", spec_tail: "char list", split: "str option" = None) -> "(token option * string) option":
        token = ""
        if inp:
            x, *xs = inp
            if x in spec_head:
                token += x
                while xs:
                    x, *xs = xs
                    if x in spec_tail:
                        token += x
                    else:
                        if split and x == split:
                            token += x
                        else:
                            xs = [x] + xs
                            break
                return chunk(token), xs
            return None
        return None
    
    def lex_spec(self, chunk: "string -> token", inp: "string", spec: "{string : string list}") -> "(token option * string) option":
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
    
    def lex_bracket(self, chunk: "(string * string * string) -> token", inp: "string", spec_left: "{string : string list}", spec_right: "{string : string list}") -> "(token option * string) option":
        # TODO support "\""
        match_left_bracket = self.lex_spec(lambda i: i, inp, spec_left)
        if match_left_bracket:
            # print(match_left_bracket)
            left, left_tail = match_left_bracket
            token = ""
            if left_tail:
                # print( (repr(token), left_tail) )
                x, *xs = left_tail
                while xs:
                    if x not in spec_right.keys():
                        token += x
                        x, *xs = xs
                    else:
                        flag, _drop = self.lex_spec(lambda i: i, [x] + xs, spec_right)    
                        if flag:
                            break
                        else:
                            token += x
                            x, *xs = xs
                # else x in spec_right.keys()
                match_right_bracket = self.lex_spec(lambda i: i, [x] + xs, spec_right)
                if match_right_bracket:
                    right, right_tail = match_right_bracket
                    return chunk((left, token, right)), right_tail
                return None
            return None
        return None

    def lex_ident(self, inp, *, spec_head, spec_tail, lineno, column):
        return self.lex_seq(lambda token: Token("ident", token, lineno, column), inp, spec_head, spec_tail)
    def lex_digit(self, inp, *, spec_head, spec_tail, lineno, column):
        return self.lex_seq(lambda token: Token("digit", token, lineno, column), inp, spec_head, spec_tail, ".")
    def lex_skip(self, inp, *, spec, lineno, column):
        return self.lex_spec(lambda token: Token("skip", token, lineno, column), inp, spec)
    def lex_symbol(self, inp, *, spec, lineno, column):
        return self.lex_spec(lambda token: Token("symbol", token, lineno, column), inp, spec)
    def lex_keyword(self, inp, *, spec, lineno, column):
        return self.lex_spec(lambda token: Token("keyword", token, lineno, column), inp, spec)
    def lex_label_bracket(self, inp, *, label, spec_left, spec_right, lineno, column):
        return self.lex_bracket(lambda token: Token(label, token, lineno, column), inp, spec_left, spec_right)

    def lex(self, inp, *, ident_spec_head, ident_spec_tail, digit_spec, skip_spec, symbol_spec, keyword_spec, label_bracket_dict):
        c = 0
        old_inp = inp
        while inp:
            lineno = old_inp[:c].count('\n')
            last_lineno = old_inp[:c].rfind("\n")
            column = c - last_lineno

            flag = False
            for label, (spec_left, spec_right) in label_bracket_dict.items():
                match = self.lex_label_bracket(inp, label=label, spec_left=spec_left, spec_right=spec_right, lineno=lineno, column=column)
                if match:
                    # print(match)
                    token, inp = match
                    c += len(token.value[0] + token.value[1] + token.value[2])
                    yield token
                    flag = True
                    break
            if flag:
                continue

            match = self.lex_skip(inp, spec=skip_spec, lineno=lineno, column=column)
            if match:
                # print(match)
                token, inp = match
                c += len(token.value)
                yield token
                continue

            match = self.lex_ident(inp, spec_head=ident_spec_head, spec_tail=ident_spec_tail, lineno=lineno, column=column) # ident always behind on label_bracket
            if match:
                # print(match)
                token, inp  = match
                c += len(token.value)
                yield token
                continue
            
            match = self.lex_digit(inp, spec_head=digit_spec, spec_tail=digit_spec, lineno=lineno, column=column)
            if match:
                # print(match)
                token, inp = match
                c += len(token.value)
                yield token
                continue

            match = self.lex_symbol(inp, spec=symbol_spec, lineno=lineno, column=column)
            if match:
                # print(match)    
                token, inp = match
                c += len(token.value)
                yield token
                continue

            match = self.lex_keyword(inp, spec=keyword_spec, lineno=lineno, column=column) # digit and symbol and keyword always lexical behind on ident
            if match:
                # print(match)    
                token, inp = match
                if token:
                    c += len(token.value)    
                    yield token
                    continue

            raise LexicalError(f"at Line {lineno}, Column {column}")

class Lexical(object):
    def __init__(self):
        self.ident_spec_head = list(map(chr, range(ord("A"), ord("Z") + 1))) + \
                            list(map(chr, range(ord("a"), ord("z") + 1))) + ["_", "-"]
        self.ident_spec_tail = self.ident_spec_head + [str(x) for x in range(10)]
        self.digit_spec =  [str(x) for x in range(10)]
        self.skip_spec = {}
        self.symbol_spec = {}
        self.keyword_spec = {}
        self.label_bracket_dict = {}
        self._lex = _Lexical().lex

    def construct_spec(self, symbol: "string") -> "{string : string list}":
        symbol_spec = {}
        if symbol:
            prefix = ""
            if len(symbol) == 1:
                if symbol not in symbol_spec.keys():
                    symbol_spec[symbol] = [one]
                    return symbol_spec
                else:
                    if one not in symbol_spec[symbol]:
                        symbol_spec[symbol].append(one)
                        return symbol_spec
                    return symbol_spec
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
            return symbol_spec
        return symbol_spec

    def register_spec(self, symbol, symbol_spec):
        if symbol:
            prefix = ""
            if len(symbol) == 1:
                if symbol not in symbol_spec.keys():
                    symbol_spec[symbol] = [one]
                    return
                else:
                    if one not in symbol_spec[symbol]:
                        symbol_spec[symbol].append(one)
                        return
                    return
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
            return
        else:
            raise ValueError(f"register({symbol!r}, ...)")
    def register_skip(self, skip: "string"):
        self.register_spec(skip, self.skip_spec)
    def register_symbol(self, symbol: "string"):
        self.register_spec(symbol, self.symbol_spec)
    def register_keyword(self, keyword: "string"):
        self.register_spec(keyword, self.keyword_spec)
    def register_label_bracket(self, label: "string", left: "string", right: "string"):
        if label not in self.label_bracket_dict.keys():
            self.label_bracket_dict[label] = (self.construct_spec(left), self.construct_spec(right))
        else:
            raise ValueError(f"register_label_bracket({label}) exists")

    def lex(self, inp, filters=[]):
        g = self._lex(
            inp, skip_spec=self.skip_spec, symbol_spec=self.symbol_spec, keyword_spec=self.keyword_spec, 
            ident_spec_head=self.ident_spec_head, 
            ident_spec_tail=self.ident_spec_tail,
            digit_spec=self.digit_spec,
            label_bracket_dict=self.label_bracket_dict,
        )
        for filter in filters:
            g = filter(g)
        return g
