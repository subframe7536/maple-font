import source.py.feature.ast as ast


def cv37_subst():
    return ast.subst_map(
        [
            "y",
            "yacute",
            "ycircumflex",
            "ydieresis",
            "ydotbelow",
            "ygrave",
            "yhookabove",
            "ymacron",
            "ytilde",
        ],
        target_suffix=".cv37",
    )


cv37_name = "Italic y with straight intersection"
cv37_feat_italic = ast.cv(37, cv37_name, cv37_subst())
