from source.py.feature import ast
from source.py.feature.shared.calt import (
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


def get_calt_regular(letter: list[ast.Clazz], hex: ast.Clazz):
    return [
        upper.get_lookup(),
        asciitilde.get_lookup(),
        brace.get_lookup(),
        colon.get_lookup(),
        cross.get_lookup(hex),
        equal_arrow.get_lookup(),
        equals.get_lookup(),
        escape.get_lookup(),
        hyphen_arrow.get_lookup(),
        lines.get_lookup(),
        markup_like.get_lookup(),
        multiple_compare.get_lookup(letter),
        numbersign_underscore.get_lookup(),
        tag.get_lookup(),
        whitespace.get_lookup(),
    ]


def get_calt_italic(letter: list[ast.Clazz], hex: ast.Clazz):
    return get_calt_regular(letter, hex) + italic.get_lookup()
