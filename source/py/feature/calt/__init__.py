from source.py.feature import ast
from source.py.feature.calt import (
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


def get_calt_lookup(
    cls_var: ast.Clazz, cls_hex_letter: ast.Clazz, is_italic: bool, normal: bool = False
) -> list[list[ast.Lookup]]:
    lookup = [
        whitespace.get_lookup(cls_var),
        asciitilde.get_lookup(),
        cross.get_lookup(cls_hex_letter),
        markup_like.get_lookup(),
        equal_arrow.get_lookup(cls_var),
        escape.get_lookup(),
        hyphen_arrow.get_lookup(),
        pipe.get_lookup(),
        tag.get_lookup(cls_var),
    ]

    if is_italic and not normal:
        lookup += [italic.get_lookup()]

    return lookup


def get_calt(
    cls_var: ast.Clazz, cls_hex_letter: ast.Clazz, is_italic: bool, is_normal: bool = False
) -> ast.Feature:
    return ast.Feature(
        "calt", get_calt_lookup(cls_var, cls_hex_letter, is_italic, is_normal), "7.0"
    )
