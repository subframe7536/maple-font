import source.py.feature.ast as ast


def ss10_subst():
    return [
        ast.subst_liga(
            "=~",
            target=ast.gly("=~", ".ss10"),
            ign_prefix=ast.cls("~", "<", ">", ":", "="),
            ign_suffix=ast.cls("~", "=", ">"),
        ),
        ast.subst_liga(
            "!~",
            target=ast.gly("!~", ".ss10"),
            ign_prefix="!",
            ign_suffix=ast.cls("!", "~", "=", ">"),
        ),
    ]


ss10_name = (
    "Approximately equal to and approximately not equal to ligatures (`=~`, `!~`)"
)
ss10_feat = ast.StylisticSet(
    id=10, desc=ss10_name, content=ss10_subst(), version="7.1", example="=~"
)
