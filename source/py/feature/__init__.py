from source.py.feature import ast
from source.py.feature.base import get_base_feature_cn_only
from source.py.feature.calt import get_calt_lookup
from source.py.feature.regular import (
    feature_file_regular,
    feature_file_regular_cn,
    cls_var,
    cls_hex_letter,
    cv_list_regular,
    cv_list_cn,
    ss_list_regular,
)
from source.py.feature.italic import (
    feature_file_italic,
    feature_file_italic_cn,
    cv_list_italic,
    ss_list_italic,
)
from source.py.feature.cv import cv96, cv97, cv98, cv99


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
            get_base_feature_cn_only(),
            cv96.cv96_feat_cn,
            cv97.cv97_feat_cn,
            cv98.cv98_feat_cn,
            cv99.cv99_feat_cn,
        ],
    )


def get_all_calt_text():
    result = []

    for item in ast.recursive_iterate(get_calt_lookup(cls_var, cls_hex_letter, False)):
        if isinstance(item, ast.Lookup) and item.desc:
            if item.name == "escape":
                result.append(item.desc.replace("\\ ", "\\\\ "))
            else:
                result.append(item.desc)

    return "\n".join(result)


zero_desc = "Dot style `0`"


def get_cv_desc():
    return "\n".join(
        [cv.desc_item() for cv in cv_list_regular] + [f"- zero: {zero_desc}"]
    )


def get_cv_italic_desc():
    return "\n".join(
        [cv.desc_item() for cv in cv_list_italic if cv.id > 30 and cv.id < 61]
    )


def get_cv_cn_desc():
    return "\n".join([cv.desc_item() for cv in cv_list_cn])


def get_ss_desc():
    result = {}
    for ss in ss_list_regular + ss_list_italic:
        if ss.id not in result:
            desc = ss.desc_item()

            if ss.id == 5:
                desc = desc.replace("`\\\\`", "`\\\\\\\\`")

            result[ss.id] = desc

    return "\n".join(sorted(result.values()))


__total_feat_list = (
    cv_list_regular + cv_list_italic + cv_list_cn + ss_list_regular + ss_list_italic
)


def get_total_feat() -> dict[str, str]:
    result = {}

    for item in __total_feat_list:
        if item.tag not in result:
            result[item.tag] = item.desc.replace("`", "'")

    result["zero"] = zero_desc.replace("`", "'")

    return dict(sorted(result.items()))


def get_freeze_moving_rules() -> list[str]:
    result = set()

    for feat in __total_feat_list:
        if feat.has_lookup:
            result.add(feat.tag)

    return list(result)
