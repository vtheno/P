from vlex import vlex, _filter

@vlex
def test():
    """
    %lex-skip "\\t"
    %lex-skip "\\n"
    %lex-skip " "
    %lex-keyword "let"
    %lex-keyword "in"
    %lex-keyword "if"
    %lex-keyword "then"
    %lex-keyword "else"
    %lex-keyword "let*"
    %lex-symbol "="
    %lex-symbol "::"
    %lex-symbol "++"
    %lex-label-bracket comment "--" "\\n"
    %lex-label-bracket mulit-comment "{-" "-}"
    """
print("end")
print("-" * 100)

x = test.lex("""
if a
then b
else let c = d
     in let* h = e :: f ++ g
        in h
""", [_filter])
for i in x :
    print(i)