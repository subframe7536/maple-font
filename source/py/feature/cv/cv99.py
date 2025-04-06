import source.py.feature.ast as ast
from source.py.feature.base.locl import lookup_tw_name


def cv99_subst():
    return [ast.use_lookup(lookup_tw_name)]


cv99_name = "Traditional centered punctuations"
cv99_feat_cn = ast.cv(99, cv99_name, cv99_subst())
