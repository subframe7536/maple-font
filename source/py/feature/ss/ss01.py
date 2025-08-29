from source.py.feature import ast


def ss01_subst():
    return ast.subst_map(
        [
            "==",
            "===",
            "!=",
            "!==",
            "=/=",
        ],
        target_suffix=".ss01",
    )


ss01_name = "Broken multiple equals ligatures (`==`, `===`, `!=`, `!==` ...)"
ss01_feat = ast.StylisticSet(
    id=1, desc=ss01_name, content=ss01_subst(), version="7.0", example="=="
)
