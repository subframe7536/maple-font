import source.py.feature.ast as ast


def cv02_subst():
    return ast.subst_map(
        [
            "a",
            "aacute",
            "abreve",
            "abreveacute",
            "abrevedotbelow",
            "abrevegrave",
            "abrevehookabove",
            "abrevetilde",
            "acaron",
            "acircumflex",
            "acircumflexacute",
            "acircumflexdotbelow",
            "acircumflexgrave",
            "acircumflexhookabove",
            "acircumflextilde",
            "adieresis",
            "adotbelow",
            "agrave",
            "ahookabove",
            "amacron",
            "aogonek",
            "aring",
            "atilde",
            "a-cy",
            "ordfeminine",
        ],
        target_suffix=".cv02",
    )


cv02_name = "Alternative `a` with top arm, no effect on italic `a`"
cv02_feat_regular = ast.CharacterVariant(2, cv02_name, cv02_subst())
