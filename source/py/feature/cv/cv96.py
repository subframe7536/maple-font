import source.py.feature.ast as ast


def cv96_subst():
    return ast.subst_map(
        [
            "“",
            "”",
            "‘",
            "’",
        ],
        target_suffix=".full",
    )


cv96_name = "Full width quotes (`“` / `”` / `‘` / `’`)"
cv96_feat_cn = ast.CharacterVariant(96, cv96_name, cv96_subst())
