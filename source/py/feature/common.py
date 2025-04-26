from copy import deepcopy
import source.py.feature.ast as ast
from source.py.feature.base import get_base_features
from source.py.feature.base.lang import get_lang_list
from source.py.feature.calt import get_calt
from source.py.feature.cv import cv96, cv97, cv98, cv99


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


def get_feature_file(
    class_list: list[ast.Clazz],
    cv_list: list[ast.CharacterVariant],
    ss_list: list[ast.StylisticSet],
    is_italic: bool,
    is_cn: bool,
    is_normal: bool,
    is_calt: bool,
    is_variable: bool,
):
    """
    Generates feature string.

    For ``variable=True, normal=True``, enabled features are
    moved to calt feature to freeze them.

    Please ENSURE:
    - the ``class_list[-2]`` is ``@Var``
    - the ``class_list[-1]`` is ``@HexLetter``

    Args:
        class_list (list[ast.Clazz]): List of class definitions
        cv_list (list[ast.CharacterVariant]): List of character variant features
        ss_list (list[ast.StylisticSet]): List of stylistic set features
        is_italic (bool): Whether to generate italic features
        is_cn (bool): Whether to include Chinese-specific features
        is_normal (bool): Whether to generate normal preset
        is_calt (bool): Whether to enable calt
        is_variable (bool): Whether this is for a variable font
    """
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
    if is_normal and is_variable:
        extracted_lookup_list = []
        for feat in cv_ss_list:
            if feat.tag in normal_enabled_features:
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
