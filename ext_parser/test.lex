%lex-skip "\n"
%lex-skip " "
%lex-skip "\t"
%lex-symbol "::="
%lex-label-bracket terminal "\"" "\""
%lex-label-bracket non-terminal "<" ">"      
%lex-label-bracket mapto  "|->" ";"
%lex-label-bracket header "%" "\n"
%lex-label-bracket comment "--" "\n"
%lex-label-bracket mulit-comment "{-" "-}"
-- construct lex.Token to parser.Terminal
{-
    mulit-comment is {- \-}
    BNF non-terminal using <name>
    BNF terminal using 
    "<ident>" alias to Token(type='ident')
    "<digit>" alias to Token(type='digit')
    "<label-bracket-name>" alias to Token(type="label-bracket-name")
    "::" alias to Token(type="symbol", value="::")
    "let" alias to Token(type="keyword", value="let")
-}
<terminals> ::= "<terminal>" <terminals>
<terminals> ::= "<terminal>"
<non-terminals> ::= "<non-terminal>" <non-terminals>
<non-terminals> ::= "<non-terminal>"
<symbols> ::= <terminals> <symbols>
<symbols> ::= <terminals>
<symbols> ::= <non-terminals> <symbols>
<symbols> ::= <non-terminals>
<headers> ::= "<header>" <headers>
<headers> ::= <headers>
<expr> ::= <non-terminals> "::=" <symbols> "<mapto>"
<expr> ::= <non-terminals> "::=" <symbols>
<exprs> ::= <expr> <exprs>
<exprs> ::= <expr>
<start> ::= <exprs>    -- parser result