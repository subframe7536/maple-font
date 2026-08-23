from __future__ import annotations

from dataclasses import dataclass, field

from scripts.feature import ast
from scripts.feature.calt import (
    asciitilde,
    cross,
    equal_arrow,
    escape,
    hyphen_arrow,
    italic,
    markup_like,
    pipe,
    tag,
    whitespace,
)
from scripts.feature.calt._infinite_utils import InfiniteOptions

_DEFAULT_INFINITE_OPTIONS = InfiniteOptions()


@dataclass(frozen=True)
class CaltOptions:
    is_italic: bool = False
    normal: bool = False
    enable_tag: bool = True
    remove_italic_calt: bool = False
    infinite_options: InfiniteOptions = field(default_factory=InfiniteOptions)


def get_calt_lookup(
    cls_var: ast.Clazz,
    cls_hex_letter: ast.Clazz,
    options: CaltOptions | None = None,
    *,
    is_italic: bool = False,
    normal: bool = False,
    enable_tag: bool = True,
    remove_italic_calt: bool = False,
    infinite_options: InfiniteOptions = _DEFAULT_INFINITE_OPTIONS,
) -> list[ast.FeatureContent]:
    if options is None:
        options = CaltOptions(
            is_italic=is_italic,
            normal=normal,
            enable_tag=enable_tag,
            remove_italic_calt=remove_italic_calt,
            infinite_options=infinite_options,
        )

    lookup: list[ast.FeatureContent] = [
        whitespace.get_lookup(cls_var, options.infinite_options),
        asciitilde.get_lookup(),
        cross.get_lookup(cls_hex_letter),
        markup_like.get_lookup(),
        equal_arrow.get_lookup(cls_var, options.infinite_options),
        escape.get_lookup(),
        hyphen_arrow.get_lookup(cls_var, options.infinite_options),
        pipe.get_lookup(),
    ]

    if options.enable_tag:
        lookup += [tag.get_lookup(cls_var)]

    if options.is_italic and not options.normal and not options.remove_italic_calt:
        lookup += [italic.get_lookup()]

    return lookup


def get_calt(
    cls_var: ast.Clazz,
    cls_hex_letter: ast.Clazz,
    options: CaltOptions | None = None,
    *,
    is_italic: bool = False,
    is_normal: bool = False,
    enable_tag: bool = True,
    remove_italic_calt: bool = False,
    infinite_options: InfiniteOptions = _DEFAULT_INFINITE_OPTIONS,
) -> ast.Feature:
    if options is None:
        options = CaltOptions(
            is_italic=is_italic,
            normal=is_normal,
            enable_tag=enable_tag,
            remove_italic_calt=remove_italic_calt,
            infinite_options=infinite_options,
        )

    return ast.Feature(
        "calt",
        get_calt_lookup(
            cls_var,
            cls_hex_letter,
            options,
        ),
        "7.0",
    )
