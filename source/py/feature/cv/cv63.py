import source.py.feature.ast as ast


# https://github.com/subframe7536/maple-font/issues/352
def cv63_subst():
    return ast.subst_liga(
        "~=",  # Lua
        target=ast.gly("~=", ".cv63"),
        banner=[
            ast.ignore(ast.cls("~", "<", "="), "~", "="),
            ast.ignore(None, "~", ["=", ast.cls("~", "=", ">", "<", ":")]),
        ],
    )


cv63_name = "Enable `~=` as not equal to, broken by `ss01`"
cv63_feat_regular = cv63_feat_italic = ast.CharacterVariant(63, cv63_name, cv63_subst())
