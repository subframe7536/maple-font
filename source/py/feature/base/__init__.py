import source.py.feature.ast as ast
from source.py.feature.base.case import case_feature
from source.py.feature.base.ccmp import (
    ccmp_feature,
    ccmp_features_cn,
    ccmp_features_cn_only,
)
from source.py.feature.base.number import number_features
from source.py.feature.base.locl import (
    locl_feature,
    locl_features_cn,
    lookup_tw,
    locl_features_cn_only,
)


def get_base_features(calt: ast.Feature, is_cn: bool):
    result = [case_feature] + number_features

    if is_cn:
        result = [lookup_tw, locl_features_cn] + result
    else:
        result = [locl_feature] + result

    aalt_feature = ast.Feature(
        "aalt",
        [feat.use() for feat in result + [calt] if isinstance(feat, ast.Feature)],
    )
    result = [aalt_feature] + result + [calt]

    if is_cn:
        result += [ccmp_features_cn]
    else:
        result += [ccmp_feature]

    return result


def get_base_feature_cn_only():
    return [
        lookup_tw,
        locl_features_cn_only,
        ccmp_features_cn_only,
    ]
