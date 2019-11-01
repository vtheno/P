from llex import Lexical

__all__ = ["vlex"]

_vlex = Lexical()
_vlex.register_skip(" ")
_vlex.register_skip("\n")
_vlex.register_skip("\t")

_vlex.register_label_bracket("comment", "--", "\n")
_vlex.register_label_bracket("mulit-comment", "{-", "-}")
_vlex.register_label_bracket("header", "%", "\n")
def _filter(g):
    yield from (i for i in g if i.type!="skip" and i.type!="comment" and i.type!="mulit-comment")
def _inline_filter(g):
    yield from (i for i in g if i.type!="skip")
def vlex(func):
    inp = func.__doc__
    lexical = Lexical()
    _inline_lex = Lexical() # lexical command
    _inline_lex.register_skip(" ")
    _inline_lex.register_skip("\n")
    _inline_lex.register_skip("\t")
    _inline_lex.register_label_bracket("quote", "\"", "\"")
    
    replace = lambda s: s.replace("\\n", "\n").replace("\\t", "\t") # translate \\n => \n  and \\t => \t
    g = _vlex.lex(inp, [_filter])
    for i in g:
        # print(i.type, i.value)
        if i.type == "header":
            # parser
            _, value, _ = i.value
            # in lexical \\ is \, \\n is \n
            command, *args = list(_inline_lex.lex(value, [_inline_filter]))
            # if command.value not in commands:
            #    raise Lexical parser header error
            # print( command.value, args )
            if command.value == "lex-skip":
                [(_, skip, _)] = [arg.value for arg in args]
                lexical.register_skip(replace(skip))
            elif command.value == "lex-symbol":
                [(_, symbol, _)] = [arg.value for arg in args]
                lexical.register_symbol(replace(symbol))
            elif command.value == "lex-keyword":
                [(_, keyword, _)] = [arg.value for arg in args]
                lexical.register_keyword(replace(keyword))
            elif command.value == "lex-label-bracket":
                label, (_, lsym, _), (_, rsym, _) = [arg.value for arg in args]
                lexical.register_label_bracket(label, replace(lsym), replace(rsym))
            else:
                raise LexicalError(f"invaild header: {command.value} lineno {command.lineno} column {command.column}")
    return lexical