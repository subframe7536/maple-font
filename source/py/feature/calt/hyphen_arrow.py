from source.py.feature import ast
from source.py.feature.base.clazz import digit


def get_lookup():
    return [
        ast.subst_liga(
            "<!--",
            banner=[
                ast.ignore("<", "<", ["!", "-", "-"]),
                ast.ignore(None, "<", ["!", "-", "-", "-"]),
                ast.ignore(["(", "?"], "<", ["!", "-", "-"]),
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
                ast.ignore(ast.clazz(["-", "<", ">", "|", "+"]), "-", ">"),
                ast.ignore(None, "-", [">", ">"]),
            ],
        ),
        ast.subst_liga(
            "<-",
            banner=[
                ast.ignore("<", "<", "-"),
                ast.ignore(
                    None, "<", ["-", ast.clazz(["-", "<", ">", "|", "+", "/", digit])]
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
