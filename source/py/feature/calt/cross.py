from source.py.feature import ast
from source.py.feature.base.clazz import cls_zero, cls_digit


def get_lookup(cls_hex_letter: ast.Clazz):
    return [
        # Upper x for HEX numbers and width-height expression
        ast.Lookup(
            "cross",
            "0xA12 0x56 1920x1080",
            [
                ast.subst(
                    cls_zero, "x", ast.cls(cls_digit, cls_hex_letter), "multiply"
                ),
                ast.subst(cls_digit, "x", cls_digit, "multiply"),
            ],
        )
    ]
