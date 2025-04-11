from source.py.feature import ast


def get_lookup():
    escape_cls = ast.Clazz("Escape", ast.LATIN_PUNCTUATIONS)
    escape_liga = ast.gly("\\", ".liga")
    return [
        # Thin backslash (\\) to better distingish escape chars
        ast.Lookup(
            "escape",
            "\\\\ \\\" \\.",
            [
                ast.cls_states(escape_cls),
                ast.ignore(escape_liga, "\\", escape_cls),
                ast.ignore(None, "\\", ["%", "%"]),
                ast.subst(None, "\\", escape_cls, escape_liga),
            ],
        )
    ]
