import source.py.feature.ast as ast
from source.py.feature.base.case import get_case_feature
from source.py.feature.base.ccmp import get_ccmp_feature
from source.py.feature.base.number import get_number_feature_list
from source.py.feature.base.locl import get_locl_feature_list


def get_base_features(calt: ast.Feature, is_cn: bool):
    aalt_feat_list = (
        get_locl_feature_list(cn=is_cn)
        + [get_case_feature()]
        + get_number_feature_list()
        + [calt]
    )

    aalt_feature = ast.Feature(
        "aalt",
        [feat.use() for feat in aalt_feat_list if isinstance(feat, ast.Feature)],
        "7.0",
    )

    return [aalt_feature, get_ccmp_feature(cn=is_cn)] + aalt_feat_list


def get_base_feature_cn_only():
    result = get_locl_feature_list(cn=True, cn_only=True)
    result.append(get_ccmp_feature(cn=True, cn_only=True))
    return result
