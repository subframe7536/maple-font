from source.py.feature import ast


def ss07_subst():
    return [
        ast.subst_liga(
            ">>",
            lookup_name=f"relax_{ast.gly('>>')}",
            ign_prefix=ast.cls(">", "/", "<"),
            ign_suffix=">",
        ),
        ast.subst_liga(
            ">>>",
            lookup_name=f"relax_{ast.gly('>>>')}",
            ign_prefix=">",
            ign_suffix=">",
        ),
    ]


ss07_name = "Relax the conditions for multiple greaters ligatures (`>>` or `>>>`)"
ss07_feat = ast.StylisticSet(
    id=7, desc=ss07_name, content=ss07_subst(), version="7.0", example=">>>"
)
