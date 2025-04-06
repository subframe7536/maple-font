import source.py.feature.ast as ast


def cv36_subst():
    return ast.subst_map(
        ["x", ast.gly("xl"), ast.gly("xl", ".cv04"), ast.gly("xl", ".cv35")],
        target_suffix=".cv36",
    )


cv36_name = "Italic x without top and bottom tails"
cv36_feat_italic = ast.cv(36, cv36_name, cv36_subst())
