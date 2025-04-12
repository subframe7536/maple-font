from source.py.feature import ast
from source.py.feature.base.clazz import cls_question


def get_lookup():
    return [
        ast.subst_liga(
            "==",
            banner=[
                ast.ignore(ast.cls("=", "!"), "=", "="),
                ast.ignore(None, "=", ["=", ast.cls("=", ">")]),
                ast.ignore(["(", cls_question], "=", "="),
                ast.ignore(["(", cls_question, "<"], "=", "="),
            ],
        ),
        ast.subst_liga(
            "===",
            banner=[
                ast.ignore("=", "=", ["=", "="]),
                ast.ignore(None, "=", ["=", "=", ast.cls("=", ">")]),
                ast.ignore(["(", cls_question], "=", ["=", "="]),
                ast.ignore(["(", cls_question, "<"], "=", ["=", "="]),
            ],
        ),
        ast.subst_liga(
            "!=",
            banner=[
                ast.ignore(ast.cls("!", "="), "!", "="),
                ast.ignore(None, "!", ["=", "="]),
                ast.ignore(["(", cls_question], "!", "="),
                ast.ignore(["(", cls_question, "<"], "!", "="),
            ],
        ),
        ast.subst_liga(
            "!==",
            banner=[
                ast.ignore(ast.cls("!", "="), "!", ["=", "="]),
                ast.ignore(None, "!", ["=", "=", "="]),
                ast.ignore(["(", cls_question], "!", ["=", "="]),
                ast.ignore(["(", cls_question, "<"], "!", ["=", "="]),
            ],
        ),
        ast.subst_liga(
            "=/=",
            banner=[
                ast.ignore("=", "=", ["/", "="]),
                ast.ignore(None, "=", ["/", "=", "="]),
                ast.ignore(["(", cls_question], "=", ["/", "="]),
                ast.ignore(["(", cls_question, "<"], "=", ["/", "="]),
            ],
        ),
        ast.subst_liga(
            "=!=",
            banner=[
                ast.ignore("=", "=", ["!", "="]),
                ast.ignore(None, "=", ["!", "=", "="]),
                ast.ignore(["(", cls_question], "=", ["!", "="]),
                ast.ignore(["(", cls_question, "<"], "=", ["!", "="]),
            ],
        ),
        ast.subst_liga(
            "=<=",
            banner=[
                ast.ignore(ast.cls("=", ">", "<", "|"), "=", ["<", "="]),
                ast.ignore(None, "=", ["<", "=", ast.cls("=", "<", ">")]),
                ast.ignore(["(", cls_question], "=", [">", "="]),
            ],
        ),
        ast.subst_liga(
            "=>=",
            banner=[
                ast.ignore(ast.cls("=", ">", "<", "|"), "=", [">", "="]),
                ast.ignore(None, "=", [">", "=", ast.cls("=", "<", ">")]),
                ast.ignore(["(", cls_question], "=", [">", "="]),
            ],
        ),
        ast.subst_liga(
            "|=",
            banner=[
                ast.ignore("|", "|", "="),
                ast.ignore(None, "|", ["=", ast.cls(">", "=")]),
            ],
        ),
        ast.subst_liga(
            "||=",
            banner=[
                ast.ignore("|", "|", ["|", "="]),
                ast.ignore(None, "|", ["|", "=", "="]),
            ],
        ),
    ]
