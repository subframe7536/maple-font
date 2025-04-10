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


cv37_name = "Alternative Italic `y` with straight intersection"
cv37_feat_italic = ast.CharacterVariant(37, cv37_name, cv37_subst())
