from source.py.feature import ast


def ss01_subst():
    return ast.subst_map(
        [
            "==",
            "===",
            "!=",
            "!==",
            "=/=",
            ast.gly("~=", ".cv63"),
            ast.gly("=~", ".cv64"),
            ast.gly("!~", ".cv64"),
        ],
        target_suffix=".ss01",
    )


ss01_name = "Broken multiple equals ligatures (`==`, `===`, `!=`, `!==` ...)"
ss01_feat = ast.StylisticSet(1, ss01_name, ss01_subst())
