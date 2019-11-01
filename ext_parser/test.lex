%lex-skip "\n"
%lex-skip " "
%lex-skip "\t"
%lex-symbol "::="
%lex-label terminal "\"" "\""
%lex-label non-terminal "<" ">"      
%lex-label mapto  "|->" ";"
%lex-label header "%" "\n"
%lex-label comment "--" "\n"
%lex-label mulit-comment "{-" "-}"
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
{-
mulit-comment is {- \-}
 -}
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