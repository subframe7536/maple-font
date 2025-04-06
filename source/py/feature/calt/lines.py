from source.py.feature import ast


def get_lookup():
    return [
        ast.subst_liga(
            "<|||",
            banner=[
                ast.ignore("<", "<", ["|", "|", "|"]),
                ast.ignore(None, "<", ["|", "|", "|", ast.clazz(["|", ">"])]),
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
                ast.ignore(None, "<", ["|", "|", ast.clazz(["|", ">"])]),
            ],
        ),
        ast.subst_liga(
            "||>",
            banner=[
                ast.ignore(ast.clazz(["-", "<"]), "|", ["|", ">"]),
                ast.ignore(None, "|", ["|", ">", ">"]),
            ],
        ),
        ast.subst_liga(
            "<|",
            banner=[
                ast.ignore("<", "<", "|"),
                ast.ignore(None, "<", ["|", ast.clazz(["|", ">"])]),
            ],
        ),
        ast.subst_liga(
            "|>",
            banner=[
                ast.ignore(ast.clazz(["-", "<"]), "|", ">"),
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
                ast.ignore(ast.clazz(["-", "<"]), "-", "|"),
                ast.ignore(None, "-", ["|", "|"]),
            ],
        ),
        ast.subst_liga(
            "|-",
            banner=[
                ast.ignore("|", "|", "-"),
                ast.ignore(None, "|", ["-", ast.clazz(["-", ">"])]),
            ],
        ),
        ast.subst_liga(
            "_|_",
            banner=[
                ast.ignore(ast.clazz(["_", "[", ","]), "_", ["|", "_"]),
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
