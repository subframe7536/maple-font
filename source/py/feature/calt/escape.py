from source.py.feature import ast
from source.py.feature.base.clazz import cls_comma, cls_question


def get_lookup():
    escape_cls = ast.Clazz("Escape", ast.LATIN_PUNCTUATIONS + [cls_comma, cls_question])
    escape_liga = ast.gly("\\", ".liga")
    return [
        # Thin backslash (\\) to better distingish escape chars
        ast.Lookup(
            "escape",
            "\\\\ \\' \\.",
            [
                ast.cls_states(escape_cls),
                ast.ignore(escape_liga, "\\", escape_cls),
                ast.ignore(None, "\\", ["%", "%"]),
                ast.subst(None, "\\", escape_cls, escape_liga),
            ],
        )
    ]
