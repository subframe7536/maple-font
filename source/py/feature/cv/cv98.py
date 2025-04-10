import source.py.feature.ast as ast


def cv98_subst():
    return ast.subst_map(
        "—",
        target_suffix=".full",
    )


cv98_name = "Full width emdash (`—`)"
cv98_feat_cn = ast.CharacterVariant(98, cv98_name, cv98_subst())
