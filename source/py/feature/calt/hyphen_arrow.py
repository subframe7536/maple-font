from source.py.feature import ast
from source.py.feature.base.clazz import cls_digit, cls_question


def get_lookup():
    return [
        ast.subst_liga(
            "<!--",
            banner=[
                ast.ignore("<", "<", ["!", "-", "-"]),
                ast.ignore(None, "<", ["!", "-", "-", "-"]),
                ast.ignore(["(", cls_question], "<", ["!", "-", "-"]),
            ],
        ),
        ast.subst_liga(
            "<#--",
            banner=[
                ast.ignore("<", "<", ["#", "-", "-"]),
                ast.ignore(None, "<", ["#", "-", "-", "-"]),
            ],
        ),
        ast.subst_liga("<!---->", target="xml_empty_comment.liga"),
        ast.subst_liga(
            "<->",
            banner=[
                ast.ignore("<", "<", ["-", ">"]),
                ast.ignore(None, "<", ["-", ">", ">"]),
            ],
        ),
        ast.subst_liga(
            "->",
            banner=[
                ast.ignore(ast.cls("-", "<", ">", "|", "+"), "-", ">"),
                ast.ignore(None, "-", [">", ">"]),
            ],
        ),
        ast.subst_liga(
            "<-",
            banner=[
                ast.ignore("<", "<", "-"),
                ast.ignore(
                    None, "<", ["-", ast.cls("-", "<", ">", "|", "+", "/", cls_digit)]
                ),
            ],
        ),
        ast.subst_liga(
            "-->",
            banner=[
                ast.ignore("-", "-", ["-", ">"]),
                ast.ignore(None, "-", ["-", ">", ">"]),
            ],
        ),
        ast.subst_liga(
            "<--",
            banner=[
                ast.ignore("<", "<", ["-", "-"]),
                ast.ignore(None, "<", ["-", "-", "-"]),
            ],
        ),
        ast.subst_liga(
            "<-<",
            banner=[
                ast.ignore("<", "<", ["-", "<"]),
                ast.ignore(None, "<", ["-", "<", "<"]),
            ],
        ),
        ast.subst_liga(
            ">->",
            banner=[
                ast.ignore(">", ">", ["-", ">"]),
                ast.ignore(None, ">", ["-", ">", ">"]),
            ],
        ),
        ast.subst_liga(
            "<-|",
            banner=[
                ast.ignore("<", "<", ["-", "|"]),
                ast.ignore(None, "<", ["-", "|", "|"]),
            ],
        ),
        ast.subst_liga(
            "|->",
            banner=[
                ast.ignore("|", "|", ["-", ">"]),
                ast.ignore(None, "|", ["-", ">", ">"]),
            ],
        ),
    ]
