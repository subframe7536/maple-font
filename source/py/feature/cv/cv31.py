import source.py.feature.ast as ast


def cv31_subst():
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
            # Ligature variants
            ast.gly("al"),
            ast.gly("all"),
            ast.gly("al", ".cv04"),
            ast.gly("all", ".cv04"),
        ],
        target_suffix=".cv31",
    )


cv31_name = "Alternative italic `a` with top arm"
cv31_feat_italic = ast.CharacterVariant(31, cv31_name, cv31_subst())
