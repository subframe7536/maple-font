import source.py.feature.ast as ast


def cv64_subst():
    return [
        ast.subst_liga(
            "=~",
            target=ast.gly("=~", ".cv64"),
            banner=[
                ast.ignore(ast.cls("~", "<", ">", ":", "="), "=", "~"),
                ast.ignore(None, "=", ["~", ast.cls("~", "=", ">")]),
            ],
        ),
        ast.subst_liga(
            "!~",
            target=ast.gly("!~", ".cv64"),
            banner=[
                ast.ignore("!", "!", "~"),
                ast.ignore(None, "!", ["~", ast.cls("!", "~", "=", ">")]),
            ],
        ),
    ]


cv64_name = (
    "Enable `=~` and `!~` as approximately equal to and not equal to, broken by `ss01`"
)
cv64_feat_regular = cv64_feat_italic = ast.CharacterVariant(64, cv64_name, cv64_subst())
