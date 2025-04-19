import source.py.feature.ast as ast


sfx = ".cv01"


def cv01_subst():
    return [
        ast.subst_map(
            "$",
            target_suffix=sfx,
        ),
        ast.subst_map(
            "%",
            target_suffix=sfx,
        ),
        ast.subst_map(
            ["&", "&&", "&&&"],
            target_suffix=sfx,
        ),
        ast.subst_map(
            ["@", "~@"],
            target_suffix=sfx,
        ),
        ast.subst_map(
            ["Q", "Q.bg"],
            target_suffix=sfx,
        ),
        ast.subst_map(
            [
                "=>",
                "<==",
                "==>",
                "<=>",
                "<==>",
                "<=<",
                ">=>",
                "<=|",
                "|=>",
                "<-|",
                "|->",
                "<-",
                "->",
                "<--",
                "-->",
                "<-<",
                ">->",
                "<->",
                "<!--",
                "<#--",
                "xml_empty_comment.liga",  # <!---->
            ],
            target_suffix=sfx,
        ),
    ]


cv01_desc = "Normalize special symbols (`@ $ & % Q => ->`)"
cv01_feat_regular = cv01_feat_italic = ast.CharacterVariant(1, cv01_desc, cv01_subst())
