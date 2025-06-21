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
            "u-cy",
            "ushort-cy",
            "umacron-cy",
            "udieresis-cy",
            "uacutedbl-cy",
        ],
        target_suffix=".cv37",
    )


cv37_name = "Alternative Italic `y` with straight intersection"
cv37_feat_italic = ast.CharacterVariant(
    id=37, desc=cv37_name, content=cv37_subst(), version="7.0", example="y"
)
