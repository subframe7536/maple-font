import source.py.feature.ast as ast


def cv61_subst():
    return ast.subst_map(
        [",", ";", ";;", ";;;"],
        target_suffix=".cv61",
    )


cv61_name = "Alternative `,` and `;` with straight tail"
cv61_feat_regular = cv61_feat_italic = ast.CharacterVariant(61, cv61_name, cv61_subst())
