from source.py.feature import ast
from source.py.feature.base.clazz import zero, digit


def get_lookup(cls_hex_letter: ast.Clazz):
    return [
        ast.lookup(
            "cross",
            "Upper x for HEX numbers and width-height expression",
            [
                # 0xA12 0x56
                ast.subst(zero, "x", ast.clazz([digit, cls_hex_letter]), "multiply"),
                # 1920x1080
                ast.subst(digit, "x", digit, "multiply"),
            ],
        )
    ]
