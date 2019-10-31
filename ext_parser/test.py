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

print(llex.symbol_spec)

print(llex.keyword_spec)
llex.register_skip(" ")
llex.register_skip("\n")
llex.register_skip("\t")
print(llex.skip_spec)

llex.register_label_bracket("comment", "--", "\n")
llex.register_label_bracket("mulit-comment", "{-", "-}")
llex.register_label_bracket("mapto", "|->", ";")
llex.register_label_bracket("non-termianl", "<", ">")
llex.register_label_bracket("terminal", "\"", "\"")
llex.register_label_bracket("header", "%", "\n")

print(llex.label_bracket_dict)

print(llex.ident_spec_head)
print(llex.ident_spec_tail)

def filter_skip(g):
    yield from (i for i in g if i.type!="skip" and i.type!="comment" and i.type!="mulit-comment")
"""
{- 
    parser.NonTerminal is non-terminal
    parser.Terminal    is terminal
-}
"""
ret = llex.lex(r"""
%lex-skip "\n"
%lex-skip " "
%lex-skip "\t"
%lex-symbol "::="
%lex-label terminal "terminal" "\"" "\""
%lex-label non-terminal "non-terminal" "<" ">"      
%lex-label mapto  "|->" ";"
%lex-label header "%" "\n"
%lex-label comment "--" "\n"
%lex mulit-comment "{-" "-}"
-- %lex-label is no finished TODO this. 

-- construct llex.Token to lparser.Label
-- %map-symbol <Token.value> <Label.value> if Token.type == Label.type == symbol
-- %map-keyword <Token.value> <Label.value> if Token.type == Label.type == keyword
-- %map-label <Token.type> <Label.type>
-- %map-ident ...
%map-symbol "::=" "::="
%map-label terminal "terminal" 
%map-label non-terminal "non-terminal"
%map-label mapto "mapto"
%map-label header "header"

<terminals> ::= "terminal" <terminals>
<terminals> ::= "terminal"
<non-terminals> ::= "non-terminal" <non-terminals>
<non-terminals> ::= "non-terminal"
<symbols> ::= <terminals> <symbols>
<symbols> ::= <terminals>
<symbols> ::= <non-terminals> <symbols>
<symbols> ::= <non-terminals>
<headers> ::= "header" <headers>
<headers> ::= <headers>
<expr> ::= <non-terminals> "::=" <symbols> "mapto"
<expr> ::= <non-terminals> "::=" <symbols>
<exprs> ::= <expr> <exprs>
<exprs> ::= <expr>
<start> ::= <exprs>    -- parser result
""", [
    filter_skip
])
"""
{-
    <exprs> ::= <expr> | <expr> <exprs> -- equal
    <exprs> ::= <expr> [<exprs>]        -- equal
-}
"""
for i in list(ret):
    print(i)

# TODO Token translate to Label (for parser), 
# TODO BNF inline another local BNF