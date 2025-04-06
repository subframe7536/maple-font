import source.py.feature.ast as ast


sfx = ".cv01"


def cv01_subst():
    return [
        ast.subst_map(
            "Q",
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
            "$",
            target_suffix=sfx,
        ),
        ast.subst_map(
            "%",
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


cv01_name = "Normalize Special Symbols"
cv01_feat_regular = ast.cv(1, cv01_name, cv01_subst())
cv01_feat_italic = ast.cv(1, cv01_name, cv01_subst())
