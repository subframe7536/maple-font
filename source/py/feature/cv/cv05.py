import source.py.feature.ast as ast


def cv05_subst():
    return ast.subst_map(
        [
            ",",
            ";",
            ";;",
            ";;;"
        ],
        target_suffix=".cv05",
    )


cv05_name = "Alternative `,` and `;` with straight tail"
cv05_feat_regular = cv05_feat_italic = ast.CharacterVariant(5, cv05_name, cv05_subst())
