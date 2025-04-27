from copy import deepcopy
import json
from source.py.feature import ast
from source.py.feature.base import get_base_feature_cn_only, get_base_features
from source.py.feature.base.lang import get_lang_list
from source.py.feature.calt import get_calt, get_calt_lookup
from source.py.feature.cv import cv96, cv97, cv98, cv99
from source.py.feature.regular import (
    cls_var,
    cls_hex_letter,
    class_list_regular,
    cv_list_regular,
    ss_list_regular,
)
from source.py.feature.italic import (
    class_list_italic,
    cv_list_italic,
    ss_list_italic,
)

normal_enabled_features = [
    "cv01",
    "cv02",
    "cv33",
    "cv34",
    "cv35",
    "cv36",
    "cv61",
    "cv62",
    "ss05",
    "ss06",
    "ss07",
    "ss08",
]


cv_list_cn = [
    cv96.cv96_feat_cn,
    cv97.cv97_feat_cn,
    cv98.cv98_feat_cn,
    cv99.cv99_feat_cn,
]


def generate_fea_string(
    is_italic: bool,
    is_cn: bool,
    is_normal: bool = False,
    is_calt: bool = True,
    variable_enabled_feature_list: list[str] | None = None,
):
    """
    Generates feature string.

    For ``variable=True, normal=True``, enabled features are
    moved to calt feature to freeze them.

    Args:
        is_italic (bool): Whether to generate italic features
        is_cn (bool): Whether to include Chinese-specific features
        is_normal (bool): Whether to generate normal preset
        is_calt (bool): Whether to enable calt
        variable_enabled_feature_list (list[str]): List of features that
            be enabled in variable format
    """
    print(
        f"Generating feature string with italic={is_italic}, cn={is_cn}, normal={is_normal}, calt={is_calt}, variable={bool(variable_enabled_feature_list)}"
    )

    class_list = class_list_italic if is_italic else class_list_regular
    cv_list = cv_list_italic if is_italic else cv_list_regular
    ss_list = ss_list_italic if is_italic else ss_list_regular

    if class_list[-2].name != "Var" or class_list[-1].name != "HexLetter":
        raise TypeError("Invalid class_list, must ends with [@Var, @HexLetter]")

    calt_feat = get_calt(
        class_list[-2], class_list[-1], is_italic=is_italic, is_normal=is_normal
    )

    # clear calt for no ligature
    if not is_calt:
        calt_feat.content = []

    cv_ss_list = deepcopy(cv_list + (cv_list_cn if is_cn else []) + ss_list)

    # for variable font, freeze feature by moving it to `calt`
    if variable_enabled_feature_list:
        extracted_lookup_list = []
        for feat in cv_ss_list:
            if feat.tag in variable_enabled_feature_list or []:
                # prevent features that add ligatures like `ss08`
                if not is_calt and feat.has_lookup:
                    continue

                extracted_lookup_list.append(
                    feat.content
                    if feat.has_lookup
                    else [ast.Lookup(f"move_{feat.tag}", None, feat.content)]
                )

                # cleanup
                feat.content = []

        calt_feat.content.extend(extracted_lookup_list)

    # remove calt if empty, to prevent fonttools warning
    if not calt_feat.content:
        calt_feat = None

    return ast.create(
        [
            class_list,
            get_lang_list(),
            get_base_features(calt_feat, is_cn=is_cn),
            cv_ss_list,
        ],
    )


def generate_fea_string_cn_only():
    return ast.create(
        [
            get_base_feature_cn_only(),
            cv_list_cn,
        ],
    )


def get_all_calt_text():
    result = []

    for item in ast.recursive_iterate(get_calt_lookup(cls_var, cls_hex_letter, True)):
        if isinstance(item, ast.Lookup) and item.desc:
            if item.name == "escape":
                result.append(item.desc.replace("\\ ", "\\\\ "))
            else:
                result.append(item.desc)

    return "\n".join(result)


zero_desc = "Dot style `0`"


def get_version_info(
    features: list[ast.CharacterVariant] | list[ast.StylisticSet],
) -> dict[str, dict[str, str]]:
    result = {}
    for item in features:
        if item.version not in result:
            result[item.version] = {}
        result[item.version][item.tag] = item.sample
    return result


def get_cv_desc():
    return "\n".join(
        [cv.desc_item() for cv in cv_list_regular] + [f"- [v7.0] zero: {zero_desc}"]
    )


def get_cv_version_info() -> dict[str, dict[str, str]]:
    return get_version_info(cv_list_regular)


def get_cv_italic_desc():
    return "\n".join(
        [cv.desc_item() for cv in cv_list_italic if cv.id > 30 and cv.id < 61]
    )


def get_cv_italic_version_info() -> dict[str, dict[str, str]]:
    return get_version_info([cv for cv in cv_list_italic if cv.id > 30 and cv.id < 61])


def get_cv_cn_desc():
    return "\n".join([cv.desc_item() for cv in cv_list_cn])


def get_cv_cn_version_info() -> dict[str, dict[str, str]]:
    return get_version_info(cv_list_cn)


def get_ss_desc():
    result = {}
    for ss in ss_list_regular + ss_list_italic:
        if ss.id not in result:
            desc = ss.desc_item()

            if ss.id == 5:
                desc = desc.replace("`\\\\`", "`\\\\\\\\`")

            result[ss.id] = desc

    return "\n".join(sorted(result.values()))


def get_ss_version_info() -> dict[str, dict[str, str]]:
    ss = list({s.tag: s for s in ss_list_regular + ss_list_italic}.values())
    return get_version_info(sorted(ss, key=lambda x: x.tag))


__total_feat_list = (
    cv_list_regular + cv_list_italic + cv_list_cn + ss_list_regular + ss_list_italic
)


def get_total_feat_dict() -> dict[str, str]:
    result = {}

    for item in __total_feat_list:
        if item.tag not in result:
            result[item.tag] = f"[v{item.version}] " + item.desc.replace("`", "'")

    result["zero"] = "[v7.0] " + zero_desc.replace("`", "'")

    return dict(sorted(result.items()))


def get_total_feat_ts() -> str:
    feat_dict = {}

    for item in __total_feat_list:
        if item.tag not in feat_dict:
            feat_dict[item.tag] = item.desc

    feat_dict["calt"] = "Default ligatures"
    feat_dict["zero"] = zero_desc

    feat_dict = dict(sorted(feat_dict.items()))

    js_object = "\n"
    for key, val in feat_dict.items():
        js_object += f"  /** {val} */\n  {key}: string\n"

    return f"""// Auto generated by `python task.py fea`
// @prettier-ignore
/* eslint-disable */

export interface FeatureDescription {{{js_object}}}

export const featureArray = {json.dumps(list(feat_dict.keys()), indent=2)}
"""


def get_freeze_moving_rules() -> list[str]:
    result = set()

    for feat in __total_feat_list:
        if feat.has_lookup:
            result.add(feat.tag)

    return list(result)
