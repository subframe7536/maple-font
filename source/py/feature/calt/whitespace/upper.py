from source.py.feature import ast
from source.py.feature.base.clazz import digit, uppercase


def get_lookup():
    dbls = "germandbls"
    dbls_calt = f"{dbls}.calt"
    return [
        ast.Lookup(
            "uppercase_colon",
            None,
            [
                ast.subst(
                    ast.cls(digit, uppercase),
                    ":",
                    ast.cls(digit, uppercase),
                    ast.gly(":", ".case"),
                )
            ],
        ),
        ast.Lookup(
            "uppercase_sharp_s",
            None,
            [
                ast.subst([uppercase, uppercase], dbls, None, dbls_calt),
                ast.subst(None, dbls, uppercase, dbls_calt),
            ],
        ),
    ]
