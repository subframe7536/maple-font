from source.py.feature import ast
from source.py.feature.calt import (
    asciitilde,
    brace,
    colon,
    cross,
    equal_arrow,
    equals,
    escape,
    hyphen_arrow,
    italic,
    lines,
    markup_like,
    multiple_compare,
    numbersign_underscore,
    tag,
    upper,
    whitespace,
)


def get_calt_regular(cls_var: ast.Clazz, cls_hex_letter: ast.Clazz):
    return [
        upper.get_lookup(),
        asciitilde.get_lookup(),
        brace.get_lookup(),
        colon.get_lookup(),
        cross.get_lookup(cls_hex_letter),
        equal_arrow.get_lookup(cls_var),
        equals.get_lookup(),
        escape.get_lookup(),
        hyphen_arrow.get_lookup(),
        lines.get_lookup(),
        markup_like.get_lookup(),
        multiple_compare.get_lookup(cls_var),
        numbersign_underscore.get_lookup(),
        tag.get_lookup(),
        whitespace.get_lookup(),
    ]


def get_calt_italic(cls_var: ast.Clazz, cls_hex_letter: ast.Clazz):
    return get_calt_regular(cls_var, cls_hex_letter) + italic.get_lookup()
