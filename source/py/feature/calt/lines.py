from source.py.feature import ast
from source.py.feature.base.clazz import cls_comma

def get_lookup():
    return [
        ast.subst_liga(
            "<|||",
            banner=[
                ast.ignore("<", "<", ["|", "|", "|"]),
                ast.ignore(None, "<", ["|", "|", "|", ast.cls("|", ">")]),
            ],
        ),
        ast.subst_liga(
            "|||>",
            banner=[
                ast.ignore("|", "|", ["|", "|", ">"]),
                ast.ignore(None, "|", ["|", "|", ">", ">"]),
            ],
        ),
        ast.subst_liga(
            "<||",
            banner=[
                ast.ignore("<", "<", ["|", "|"]),
                ast.ignore(None, "<", ["|", "|", ast.cls("|", ">")]),
            ],
        ),
        ast.subst_liga(
            "||>",
            banner=[
                ast.ignore(ast.cls("-", "<"), "|", ["|", ">"]),
                ast.ignore(None, "|", ["|", ">", ">"]),
            ],
        ),
        ast.subst_liga(
            "<|",
            banner=[
                ast.ignore("<", "<", "|"),
                ast.ignore(None, "<", ["|", ast.cls("|", ">")]),
            ],
        ),
        ast.subst_liga(
            "|>",
            banner=[
                ast.ignore(ast.cls("-", "<", "|"), "|", ">"),
                ast.ignore(None, "|", [">", ">"]),
            ],
        ),
        ast.subst_liga(
            "<|>",
            banner=[
                ast.ignore("<", "<", ["|", ">"]),
                ast.ignore(None, "<", ["|", ">", ">"]),
            ],
        ),
        ast.subst_liga(
            "-|",
            banner=[
                ast.ignore(ast.cls("-", "<"), "-", "|"),
                ast.ignore(None, "-", ["|", "|"]),
            ],
        ),
        ast.subst_liga(
            "|-",
            banner=[
                ast.ignore("|", "|", "-"),
                ast.ignore(None, "|", ["-", ast.cls("-", ">")]),
            ],
        ),
        ast.subst_liga(
            "_|_",
            banner=[
                ast.ignore(ast.cls("_", "[", cls_comma), "_", ["|", "_"]),
                ast.ignore(None, "_", ["|", "_", "_"]),
            ],
        ),
        ast.subst_liga(
            "||-",
            banner=[
                ast.ignore("|", "|", ["|", "-"]),
                ast.ignore(None, "|", ["|", "-", "-"]),
            ],
        ),
    ]
