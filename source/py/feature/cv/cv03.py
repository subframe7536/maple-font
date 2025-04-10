import source.py.feature.ast as ast


def cv03_subst():
    return ast.subst_map(
        [
            "i",
            "iacute",
            "ibreve",
            "icaron",
            "icircumflex",
            "idieresis",
            "idotaccent",
            "idotbelow",
            "idotless",
            "igrave",
            "ihookabove",
            "imacron",
            "iogonek",
            "itilde",
        ],
        target_suffix=".cv03",
    )


cv03_name = "Alternative `i` without left bottom bar"
cv03_feat_regular = ast.CharacterVariant(3, cv03_name, cv03_subst())
