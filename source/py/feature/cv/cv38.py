import source.py.feature.ast as ast


def cv38_subst():
    return ast.subst_map(
        [

            "g",
            "gacute",
            "gbreve",
            "gcaron",
            "gcircumflex",
            "gcommaaccent",
            "gdotaccent",
        ],
        target_suffix=".cv38",
    )


cv38_name = "Alternative italic `g` in double story style"
cv38_feat_italic = ast.CharacterVariant(38, cv38_name, cv38_subst())
