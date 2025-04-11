from source.py.feature import ast
from source.py.feature.base.clazz import zero, digit


def get_lookup(cls_hex_letter: ast.Clazz):
    return [
        # Upper x for HEX numbers and width-height expression
        ast.Lookup(
            "cross",
            "0xA12 0x56 1920x1080",
            [
                ast.subst(zero, "x", ast.cls(digit, cls_hex_letter), "multiply"),
                ast.subst(digit, "x", digit, "multiply"),
            ],
        )
    ]
