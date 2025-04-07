import source.py.feature.ast as ast
from source.py.feature.base.case import case_feature
from source.py.feature.base.ccmp import ccmp_feature, ccmp_features_cn
from source.py.feature.base.number import number_features
from source.py.feature.base.locl import locl_feature, locl_features_cn


aalt_feature = ast.feature(
    "aalt",
    [
        ast.use_feature("calt"),
        ast.use_feature("locl"),
        ast.use_feature("subs"),
        ast.use_feature("sinf"),
        ast.use_feature("sups"),
        ast.use_feature("frac"),
        ast.use_feature("ordn"),
        ast.use_feature("case"),
        ast.use_feature("zero"),
    ],
)

__features = [
    aalt_feature,
    number_features,
    case_feature,
]

base_features = [
    __features,
    ccmp_feature,
    locl_feature,
]

base_features_cn = [
    __features,
    ccmp_features_cn,
    locl_features_cn,
]
