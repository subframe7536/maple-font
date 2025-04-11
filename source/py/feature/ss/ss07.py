from source.py.feature import ast


def ss07_subst():
    return [
        ast.subst_liga(
            ">>",
            lookup_name=f"relax_{ast.gly('>>')}",
            banner=[
                ast.ignore(ast.cls(">", "/", "<"), ">", ">"),
                ast.ignore(None, ">", [">", ">"]),
            ],
        ),
        ast.subst_liga(
            ">>>",
            lookup_name=f"relax_{ast.gly('>>>')}",
            banner=[
                ast.ignore(">", ">", [">", ">"]),
                ast.ignore(None, ">", [">", ">", ">"]),
            ],
        ),
    ]


ss07_name = "Break connected strokes between italic letters (`>>` or `>>>`)"
ss07_feat = ast.StylisticSet(7, ss07_name, ss07_subst())
