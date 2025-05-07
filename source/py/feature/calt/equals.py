from source.py.feature import ast
from source.py.feature.base.clazz import cls_question


def get_lookup():
    return [
        ast.subst_liga(
            "==",
            ign_prefix=ast.cls("=", "!"),
            ign_suffix=ast.cls("=", ">"),
            extra_rules=[
                ast.ignore(["(", cls_question], "=", "="),
                ast.ignore(["(", cls_question, "<"], "=", "="),
            ],
        ),
        ast.subst_liga(
            "===",
            ign_prefix="=",
            ign_suffix=ast.cls("=", ">"),
            extra_rules=[
                ast.ignore(["(", cls_question], "=", ["=", "="]),
                ast.ignore(["(", cls_question, "<"], "=", ["=", "="]),
            ],
        ),
        ast.subst_liga(
            "!=",
            ign_prefix=ast.cls("!", "="),
            ign_suffix="=",
            extra_rules=[
                ast.ignore(["(", cls_question], "!", "="),
                ast.ignore(["(", cls_question, "<"], "!", "="),
            ],
        ),
        ast.subst_liga(
            "!==",
            ign_prefix=ast.cls("!", "="),
            ign_suffix="=",
            extra_rules=[
                ast.ignore(["(", cls_question], "!", ["=", "="]),
                ast.ignore(["(", cls_question, "<"], "!", ["=", "="]),
            ],
        ),
        ast.subst_liga(
            "=/=",
            ign_prefix="=",
            ign_suffix="=",
            extra_rules=[
                ast.ignore(["(", cls_question], "=", ["/", "="]),
                ast.ignore(["(", cls_question, "<"], "=", ["/", "="]),
            ],
        ),
        ast.subst_liga(
            "=!=",
            ign_prefix="=",
            ign_suffix="=",
            extra_rules=[
                ast.ignore(["(", cls_question], "=", ["!", "="]),
                ast.ignore(["(", cls_question, "<"], "=", ["!", "="]),
            ],
        ),
        ast.subst_liga(
            "=<=",
            ign_prefix=ast.cls("=", ">", "<", "|"),
            ign_suffix=ast.cls("=", "<", ">"),
            extra_rules=[
                ast.ignore(["(", cls_question], "=", [">", "="]),
            ],
        ),
        ast.subst_liga(
            "=>=",
            ign_prefix=ast.cls("=", ">", "<", "|"),
            ign_suffix=ast.cls("=", "<", ">"),
            extra_rules=[
                ast.ignore(["(", cls_question], "=", [">", "="]),
            ],
        ),
        ast.subst_liga(
            "|=",
            ign_prefix="|",
            ign_suffix=ast.cls(">", "="),
        ),
        ast.subst_liga(
            "||=",
            ign_prefix="|",
            ign_suffix="=",
        ),
    ]
