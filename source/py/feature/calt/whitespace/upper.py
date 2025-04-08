from source.py.feature import ast
from source.py.feature.base.clazz import digit, uppercase


def get_lookup():
    pre = ast.clazz([digit, uppercase])
    dbls = "germandbls"
    dbls_calt = f"{dbls}.calt"
    return [
        ast.lookup(
            "uppercase_colon", None, [ast.subst(pre, ":", pre, ast.gly(":", ".case"))]
        ),
        ast.lookup(
            "uppercase_sharp_s",
            None,
            [
                ast.subst([uppercase, uppercase], dbls, None, dbls_calt),
                ast.subst(None, dbls, uppercase, dbls_calt),
            ],
        ),
    ]
