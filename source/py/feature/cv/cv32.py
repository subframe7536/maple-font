import source.py.feature.ast as ast


def cv32_subst():
    return ast.subst_map(["f", ast.gly("ff")], target_suffix=".cv32")


cv32_name = "Italic f without bottom tail"
cv32_feat_italic = ast.cv(32, cv32_name, cv32_subst())
