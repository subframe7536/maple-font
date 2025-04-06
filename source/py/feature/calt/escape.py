from source.py.feature import ast


def get_lookup():
    escape_cls = ast.Clazz("Escape", list(ast.KNOWN_PUNCTUATIONS))
    escape_liga = ast.gly("\\", ".liga")
    return [
        ast.clazz_states([escape_cls]),
        ast.lookup(
            "escape",
            "Thin backslash (\\) to better distingish escape chars",
            [
                ast.ignore(escape_liga, "\\", escape_cls),
                ast.ignore(None, "\\", ["%", "%"]),
                ast.subst(None, "\\", escape_cls, escape_liga),
            ],
        )
    ]
