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
                "<=<",
                ">=>",
                "<!--",
                "<#--",
                "xml_empty_comment.liga",  # <!---->
                ast.gly_seq("<=", "sta"),
                ast.gly_seq(">=", "end"),
                ast.gly_seq("<-", "sta"),
                ast.gly_seq(">-", "end"),
            ],
            target_suffix=sfx,
        ),
    ]


cv01_desc = "Normalize special symbols (`@ $ & % Q => ->`)"
cv01_feat_regular = cv01_feat_italic = ast.CharacterVariant(
    id=1, desc=cv01_desc, content=cv01_subst(), version="7.0", example="@$&"
)
