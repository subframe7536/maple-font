from source.py.feature import ast
from source.py.feature.base.clazz import cls_digit, cls_uppercase


def get_lookup():
    dbls = "germandbls"
    dbls_calt = f"{dbls}.calt"
    return [
        ast.Lookup(
            "uppercase_colon",
            None,
            [
                ast.subst(
                    ast.cls(cls_digit, cls_uppercase),
                    ":",
                    ast.cls(cls_digit, cls_uppercase),
                    ast.gly(":", ".case"),
                )
            ],
        ),
        ast.Lookup(
            "uppercase_sharp_s",
            None,
            [
                ast.subst([cls_uppercase, cls_uppercase], dbls, None, dbls_calt),
                ast.subst(None, dbls, cls_uppercase, dbls_calt),
            ],
        ),
    ]
