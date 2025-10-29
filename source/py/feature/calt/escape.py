from source.py.feature import ast
from source.py.feature.base.clazz import cls_question


def get_lookup():
    escape_cls = ast.Clazz(
        "Escape",
        # Reference: https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Regular_expressions/Character_escape
        [
            "^",
            "$",
            '"',
            "'",
            "`",
            ".",
            "*",
            "+",
            "(",
            ")",
            "[",
            "]",
            "{",
            "}",
            "|",
            "/",
            "\\",
            cls_question,
        ],
    )
    escape_liga = ast.gly("\\", ".liga")
    return [
        # Thin backslash (\\) to better distingish escape chars
        ast.Lookup(
            "escape",
            "\\\\ \\' \\.",
            [
                ast.cls_states(escape_cls),
                ast.ign(escape_liga, "\\", escape_cls),
                ast.ign(None, "\\", ["%", "%"]),
                ast.subst(None, "\\", escape_cls, escape_liga),
            ],
        )
    ]
