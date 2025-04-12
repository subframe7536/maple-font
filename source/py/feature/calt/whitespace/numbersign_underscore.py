from source.py.feature import ast
from source.py.feature.base.clazz import cls_question

def get_lookup():
    start = ast.gly_var("#", "start")
    mid = ast.gly_var("#", "middle")
    end = ast.gly_var("#", "end")
    return [
        ast.subst_liga(
            "__",
            banner=[
                ast.ignore(ast.cls("_", "#"), "_", "_"),
                ast.ignore(None, "_", ["_", "_"]),
            ],
        ),
        ast.subst_liga(
            "#{",
            banner=[
                ast.ignore("#", "#", "{"),
                ast.ignore(None, "#", ["{", "{"]),
            ],
        ),
        ast.subst_liga(
            "#[",
            banner=[
                ast.ignore("#", "#", "["),
                ast.ignore(None, "#", ["[", "["]),
            ],
        ),
        ast.subst_liga(
            "#(",
            banner=[
                ast.ignore("#", "#", "("),
                ast.ignore(None, "#", ["(", "("]),
            ],
        ),
        ast.subst_liga(
            "#?",
            banner=[
                ast.ignore("#", "#", cls_question),
                ast.ignore(None, "#", [cls_question, cls_question]),
            ],
        ),
        ast.subst_liga(
            "#!",
            banner=[
                ast.ignore("#", "#", "!"),
                ast.ignore(None, "#", ["!", ast.cls("!", "=")]),
            ],
        ),
        ast.subst_liga(
            "#:",
            banner=[
                ast.ignore("#", "#", ":"),
                ast.ignore(None, "#", [":", ast.cls(":", "=")]),
            ],
        ),
        ast.subst_liga(
            "#=",
            banner=[
                ast.ignore("#", "#", "="),
                ast.ignore(None, "#", ["=", "="]),
            ],
        ),
        ast.subst_liga(
            "#_",
            banner=[
                ast.ignore("#", "#", "_"),
                ast.ignore(None, "#", ["_", ast.cls("_", "(")]),
            ],
        ),
        ast.subst_liga(
            "#__",
            banner=[
                ast.ignore(None, "#", ["_", "_", "_"]),
            ],
        ),
        ast.subst_liga(
            "#_(",
            banner=[
                ast.ignore(None, "#", ["_", "(", "("]),
            ],
        ),
        ast.subst_liga(
            "]#",
            banner=[
                ast.ignore("]", "]", "#"),
                ast.ignore(None, "]", ["#", "#"]),
            ],
        ),
        ast.Lookup(
            "infinity_numbersigns",
            "#######",
            [
                ast.subst(ast.cls(start, mid), "#", "#", mid),
                ast.subst(ast.cls(start, mid), "#", None, end),
                ast.subst(None, "#", "#", start),
            ],
        ),
    ]
