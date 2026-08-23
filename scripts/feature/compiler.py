from __future__ import annotations

import re
from copy import deepcopy
from dataclasses import dataclass
from html import escape
from typing import cast

from scripts.feature import ast
from scripts.feature.base import get_base_feature_cn_only, get_base_features
from scripts.feature.base.lang import get_lang_list
from scripts.feature.calt import CaltOptions, get_calt, get_calt_lookup
from scripts.feature.calt._infinite_utils import InfiniteOptions
from scripts.feature.cv import cv96, cv97, cv98, cv99
from scripts.feature.italic import (
    class_list_italic,
    cv_list_italic,
    ss_list_italic,
)
from scripts.feature.regular import (
    class_list_regular,
    cls_hex_letter,
    cls_var,
    cv_list_regular,
    ss_list_regular,
)
from scripts.utils.logging import logger

NORMAL_ENABLED_FEATURES: tuple[str, ...] = (
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
)

CJK_FEATURES: tuple[ast.FeatureWithDocs, ...] = (
    cv96.cv96_feat_cn,
    cv97.cv97_feat_cn,
    cv98.cv98_feat_cn,
    cv99.cv99_feat_cn,
)

normal_enabled_features = list(NORMAL_ENABLED_FEATURES)
cv_list_cn = list(CJK_FEATURES)


@dataclass(frozen=True)
class FeatureGenOptions:
    """Options for OpenType feature source compilation."""

    is_italic: bool = False
    is_cn: bool = False
    is_normal: bool = False
    is_calt: bool = True
    enable_infinite: bool = True
    enable_tag: bool = True
    remove_italic_calt: bool = False


def generate_fea_string(
    options: FeatureGenOptions | None = None,
    *,
    is_italic: bool = False,
    is_cn: bool = False,
    is_normal: bool = False,
    is_calt: bool = True,
    enable_infinite: bool = True,
    enable_tag: bool = True,
    remove_italic_calt: bool = False,
) -> str:
    """Generate the complete OpenType feature source for one font variant.

    Args:
        options: Feature generation options. If provided, kwargs are ignored.
        is_italic: Whether to generate italic features.
        is_cn: Whether to include Chinese-specific features.
        is_normal: Whether to use the normal glyph preset.
        is_calt: Whether to keep contextual ligature rules in ``calt``.
        enable_infinite: Whether to include infinite arrow ligature rules.
        enable_tag: Whether to include plain-text tag ligature rules.
        remove_italic_calt: Whether to remove italic-only contextual rules.

    Returns:
        The serialized feature source, including glyph classes, language
        systems, base features, stylistic variants, and contextual rules.
    """
    if options is None:
        options = FeatureGenOptions(
            is_italic=is_italic,
            is_cn=is_cn,
            is_normal=is_normal,
            is_calt=is_calt,
            enable_infinite=enable_infinite,
            enable_tag=enable_tag,
            remove_italic_calt=remove_italic_calt,
        )

    logger.debug(
        "Generate feature string: italic=%s, cn=%s, normal=%s, calt=%s, infinite=%s, tag=%s, remove_italic_calt=%s",
        options.is_italic,
        options.is_cn,
        options.is_normal,
        options.is_calt,
        options.enable_infinite,
        options.enable_tag,
        options.remove_italic_calt,
    )
    class_list = class_list_italic if options.is_italic else class_list_regular
    infinite_options = InfiniteOptions(options.enable_infinite)
    cv_list = (
        cv_list_italic(True, infinite_options)
        if options.is_italic
        else cv_list_regular(True, infinite_options)
    )
    ss_list = ss_list_italic(True) if options.is_italic else ss_list_regular(True)

    if class_list[-2].name != "Var" or class_list[-1].name != "HexLetter":
        raise TypeError("Invalid class_list, must ends with [@Var, @HexLetter]")

    calt_options = CaltOptions(
        is_italic=options.is_italic,
        normal=options.is_normal,
        enable_tag=options.enable_tag,
        remove_italic_calt=options.remove_italic_calt,
        infinite_options=infinite_options,
    )
    calt_feat = get_calt(
        cls_var=class_list[-2],
        cls_hex_letter=class_list[-1],
        options=calt_options,
    )

    # clear calt for no ligature
    if not options.is_calt:
        calt_feat.content = []

    cv_ss_list = deepcopy(cv_list + (cv_list_cn if options.is_cn else []) + ss_list)

    # Add placeholder to calt if empty, to prevent fonttools warning
    if not calt_feat.content:
        calt_feat.content = cast(
            "list[ast.Lookup | ast.Clazz | ast.Line]", ast.EMPTY_FEAT_CONTENT
        )

    return ast.create(
        [
            class_list,
            get_lang_list(),
            get_base_features(
                calt_feat, is_cn=options.is_cn, is_italic=options.is_italic
            ),
            cv_ss_list,
        ],
    )


def generate_fea_string_cn_only():
    logger.debug("Generate feature string: cn_only=True")
    return ast.create(
        [
            get_base_feature_cn_only(),
            cv_list_cn,
        ],
    )


def get_all_calt_text():
    result: list[str] = []

    calt_options = CaltOptions(
        is_italic=True,
        infinite_options=InfiniteOptions(enabled=True),
    )
    for item in ast.recursive_iterate(
        get_calt_lookup(
            cls_var,
            cls_hex_letter,
            calt_options,
        )
    ):
        if isinstance(item, ast.Lookup) and item.desc:
            if item.name == "escape":
                result.append(item.desc.replace("\\ ", "\\\\ "))
            elif item.name.startswith("infinite"):
                result.extend(item.desc.split(" "))
            elif not item.name.endswith("__"):
                result.append(item.desc)

    # Split into three columns
    third = (len(result) + 2) // 3  # Round up for numbers not divisible by 3

    # Create HTML table with three equal columns
    html_rows = ["<table>"]

    def wrap(desc: str):
        if not desc:
            return "<td></td>"
        _desc = escape(desc)
        italic_prefix = "italic "
        if _desc.startswith(italic_prefix):
            _desc = f"<em>{_desc.replace(italic_prefix, '')}</em>"
        return f"<td><code>{_desc}</code></td>"

    for i in range(third):
        col1 = wrap(result[i])
        col2 = wrap(result[i + third] if i + third < len(result) else "")
        col3 = wrap(result[i + 2 * third] if i + 2 * third < len(result) else "")
        html_rows.append(f"<tr>{col1}{col2}{col3}</tr>")

    html_rows.append("</table>")
    return "\n".join(html_rows)


zero_desc = "Zero style variant"


def get_cv_desc():
    return "\n".join(
        [cv.desc_item() for cv in cv_list_regular()] + [f"- [v7.0] zero: {zero_desc}"]
    )


italic_code_pattern = re.compile(r"`([^`]+)`")


def get_cv_italic_desc():
    return "\n".join(
        [
            italic_code_pattern.sub(r"_`\1`_", cv.desc_item())
            for cv in cv_list_italic()
            if cv.id > 30 and cv.id < 61
        ]
    )


def get_cv_cn_desc():
    return "\n".join([cv.desc_item() for cv in cv_list_cn])


def get_ss_desc():
    result = {}
    for ss in ss_list_regular() + ss_list_italic():
        if ss.id not in result:
            desc = ss.desc_item()

            if ss.id == 5:
                desc = desc.replace("`\\\\`", "`\\\\\\\\`")
            elif ss.id == 6:
                desc = italic_code_pattern.sub(r"_`\1`_", desc)

            result[ss.id] = desc

    return "\n".join(sorted(result.values()))


__total_feat_list = (
    cv_list_regular()
    + cv_list_italic()
    + cv_list_cn
    + ss_list_regular()
    + ss_list_italic()
)


def get_total_feat_dict() -> dict[str, str]:
    result = {}

    for item in __total_feat_list:
        if item.tag not in result:
            result[item.tag] = f"[v{item.version}] " + item.desc.replace("`", "'")

    result["zero"] = "[v7.0] " + zero_desc.replace("`", "'")

    return dict(sorted(result.items()))


def get_freeze_moving_rules() -> list[str]:
    result = set()

    for feat in __total_feat_list:
        if feat.has_lookup:
            result.add(feat.tag)

    return list(result)
