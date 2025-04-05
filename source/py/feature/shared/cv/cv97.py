import source.py.feature.ast as ast


def cv97_subst():
    return ast.subst_map(
        "…",
        target_suffix=".full",
    )


cv97_name = "Full width ellipse"
cv97_feat_cn = ast.cv(97, cv97_name, cv97_subst())
