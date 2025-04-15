import source.py.feature.ast as ast


def ss10_subst():
    return [
        ast.subst_liga(
            "=~",
            target=ast.gly("=~", ".ss10"),
            banner=[
                ast.ignore(ast.cls("~", "<", ">", ":", "="), "=", "~"),
                ast.ignore(None, "=", ["~", ast.cls("~", "=", ">")]),
            ],
        ),
        ast.subst_liga(
            "!~",
            target=ast.gly("!~", ".ss10"),
            banner=[
                ast.ignore("!", "!", "~"),
                ast.ignore(None, "!", ["~", ast.cls("!", "~", "=", ">")]),
            ],
        ),
    ]


ss10_name = (
    "Approximately equal to and approximately not equal to ligatures (`=~`, `!~`)"
)
ss10_feat = ast.StylisticSet(10, ss10_name, ss10_subst())
