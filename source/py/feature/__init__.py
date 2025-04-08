from source.py.feature import ast
from source.py.feature.regular import feature_file_regular, feature_file_regular_cn
from source.py.feature.italic import feature_file_italic, feature_file_italic_cn
from source.py.feature.cv import cv96, cv97, cv98, cv99
from source.py.feature.base.locl import locl_features_cn_only
from source.py.feature.base.ccmp import ccmp_features_cn_only


def generate_fea_string(italic: bool, cn: bool):
    if italic:
        if cn:
            return feature_file_italic_cn
        else:
            return feature_file_italic
    else:
        if cn:
            return feature_file_regular_cn
        else:
            return feature_file_regular


def generate_fea_string_cn_only():
    return ast.create(
        [
            locl_features_cn_only,
            ccmp_features_cn_only,
            cv96.cv96_feat_cn,
            cv97.cv97_feat_cn,
            cv98.cv98_feat_cn,
            cv99.cv99_feat_cn,
        ],
    )
