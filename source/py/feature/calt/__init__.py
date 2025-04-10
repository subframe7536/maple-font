from source.py.feature import ast
from source.py.feature.calt import (
    asciitilde,
    cross,
    equal_arrow,
    equals,
    escape,
    hyphen_arrow,
    italic,
    lines,
    markup_like,
    tag,
    whitespace,
)


def get_calt_lookup(
    cls_var: ast.Clazz, cls_hex_letter: ast.Clazz, is_italic: bool
) -> list[list[ast.Lookup]]:
    lookup = [
        whitespace.get_lookup(cls_var),
        asciitilde.get_lookup(),
        cross.get_lookup(cls_hex_letter),
        equal_arrow.get_lookup(cls_var),
        equals.get_lookup(),
        escape.get_lookup(),
        hyphen_arrow.get_lookup(),
        lines.get_lookup(),
        markup_like.get_lookup(),
        tag.get_lookup(),
    ]

    if is_italic:
        lookup += [italic.get_lookup()]

    return lookup


def get_calt(
    cls_var: ast.Clazz, cls_hex_letter: ast.Clazz, is_italic: bool
) -> ast.Feature:
    return ast.Feature("calt", get_calt_lookup(cls_var, cls_hex_letter, is_italic))
