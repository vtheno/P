from vlex import vlex

@vlex
def rbnf():
    r"""
    %lex-skip " "
    %lex-skip "\n"
    %lex-symbol ";"
    %lex-skip "\t"
    %lex-symbol "::="
    %lex-label-bracket comment "--" "\n"
    %lex-label-bracket mulit-comment "{-" "-}"
    %lex-label-bracket terminal "\"" "\""
    %lex-label-bracket non-terminal "<" ">"
    """

def rbnf_skip(g):
    yield from (i for i in g if i.type!="skip")

g = rbnf.lex("""
<expr> ::= <expr> "+" <expr>;
<expr> ::= <expr> "-" <expr>;
<expr> ::= <expr> "*" <expr>;
<expr> ::= <expr> "/" <expr>;
<expr> ::= "<digit>";
""", [
    rbnf_skip
])
for x in g:
    print(x)