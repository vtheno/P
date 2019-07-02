#!python
from lex import *
from pprint import pprint as print



inp = """
[{% namespace %}].{% name %} {
    display: flex;
    justify-content: {% value of xxx %};
}
<div class="{% name %}" space="{% namespace %}">
</div>
=> == ===
-- this is an skips
"""

ops = {
    "=": ["=", ">"], # two op
    "==": ["="] # three op
}
parent = [
    Pair("comment",
        { "-": ["-"], },
        { "\n": [],   }),
    Pair("template",
        { "{": ["%"], },
        { "%": ["}"], })
]
print( list(lex(inp, ops=ops, parent=parent)) )
# add new support with Parser
