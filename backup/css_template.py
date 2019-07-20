#!python
from lex import *


inp = """
[{% namespace %}].{% name %} {
    display: flex;
    justify-content: {% value of xxx %};
}
<div class="{% name %}" space="{% namespace %}">
</div>
=> == ===
-- this is an skips
1.2333
1.2
1.
"""


def Compile(template: str):
    ops = { }
    parent = [
        Pair("comment",
             { "-": ["-"], },
             { "\n": [],   }),
        Pair("template",
             { "{": ["%"], },
             { "%": ["}"], })
    ]

    generate = lex(template, ops=ops, parent=parent)
    ret = []
    for s in generate: #  for block
        if s.tag == "template":
            print(s)
        elif s.tag == "comment":
            continue
        else:
            ret.append(s)
    return ret

output = Compile(inp)
print( "[output]", output )
