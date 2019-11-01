from llex import Token, Lexical, LexicalError
"""
-- builtin terminal type: ident, digit, symbol, keyword, {- user defined label bracket -}
-- terminal: eof, ident, digit, "...":symbol, "...":keyword, custom_label
-- non-terminal with quote and <NAME>
%require <name>              -- require a <ident>
%assoc <symbol> <left|right> -- assoc header require a symbol and left or right, non-declare symbol default associate is left
%level <symbol> <digit>      -- level header require a symbol and a int digit.

-- example begin
%level + 4
%level - 4
Expr ::= Expr "+":symbol Expr  |-> 
    fn(first: Expr, sencond: token, third: Expr)
;
Expr ::= Expr "-":symbol Expr  |->
;
"""
llex = Lexical()
llex.register_symbol("::=")

# print(llex.symbol_spec)

# print(llex.keyword_spec)
llex.register_skip(" ")
llex.register_skip("\n")
llex.register_skip("\t")
# print(llex.skip_spec)

llex.register_label_bracket("comment", "--", "\n")
llex.register_label_bracket("mulit-comment", "{-", "-}")
llex.register_label_bracket("mapto", "|->", ";")
llex.register_label_bracket("non-termianl", "<", ">")
llex.register_label_bracket("terminal", "\"", "\"")
llex.register_label_bracket("header", "%", "\n")

# print(llex.label_bracket_dict)

# print(llex.ident_spec_head)
# print(llex.ident_spec_tail)

def filter_skip(g):
    yield from (i for i in g if i.type!="skip" and i.type!="comment" and i.type!="mulit-comment")
"""
{- 
    parser.NonTerminal is non-terminal
    parser.Terminal    is terminal
-}
"""
"""
{-
    <exprs> ::= <expr> | <expr> <exprs> -- equal
    <exprs> ::= <expr> [<exprs>]        -- equal
-}
"""

def parser_lexical(g):
    _lex = Lexical() # lexical command
    _lex.register_skip(" ")
    _lex.register_skip("\n")
    _lex.register_skip("\t")
    _lex.register_label_bracket("quote", "\"", "\"")
    _rlex = Lexical()
    replace = lambda s: s.replace("\\n", "\n").replace("\\t", "\t") # translate \\n => \n  and \\t => \t
    for i in g:
        if i.type == "header":
            # parser
            _, value, _ = i.value
            # in lexical \\ is \
            # \\n is \n
            command, *args = list(_lex.lex(value, [filter_skip]))
            # if command.value not in commands:
            #    raise Lexical parser header error
            # print( command.value, args )
            if command.value == "lex-skip":
                [(_, skip, _)] = [arg.value for arg in args]
                _rlex.register_skip(replace(skip))
            elif command.value == "lex-symbol":
                [(_, symbol, _)] = [arg.value for arg in args]
                _rlex.register_symbol(replace(symbol))
            elif command.value == "lex-keyword":
                [(_, keyword, _)] = [arg.value for arg in args]    
                _rlex.register_keyword(replace(keyword))
            elif command.value == "lex-label":
                label, (_, lsym, _), (_, rsym, _) = [arg.value for arg in args]
                _rlex.register_label_bracket(label, replace(lsym), replace(rsym))
    return _rlex

with open("test.lex", "r", encoding="utf8") as file:
    data = file.read()
    ret = llex.lex(data, [
        filter_skip,
    ])
    rlex = parser_lexical(ret)
    v = rlex.lex(data, [filter_skip])
    for x in v:
        print(x)
# TODO Token translate to Label (for parser), 
# TODO BNF inline another local BNF