import source.py.feature.ast as ast


def cv33_subst():
    return ast.subst_map(
        [
            "i",
            "iacute",
            "ibreve",
            "icaron",
            "icircumflex",
            "idieresis",
            "idotbelow",
            "idotless",
            "igrave",
            "ihookabove",
            "imacron",
            "iogonek",
            "itilde",
            "j",
            "jcircumflex",
            "jdotless",
            ast.gly("il"),
            ast.gly("ill"),
            ast.gly("il", ".cv04"),
            ast.gly("ill", ".cv04"),
        ],
        target_suffix=".cv33",
    )


cv33_name = "Alternative Italic `i` and `j` with left bottom bar and horizen top bar"
cv33_feat_italic = ast.CharacterVariant(33, cv33_name, cv33_subst())
