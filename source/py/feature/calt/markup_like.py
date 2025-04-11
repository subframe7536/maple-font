from source.py.feature import ast


def get_lookup():
    return [
        ast.subst_liga(
            "<>",
            banner=[
                ast.ignore("<", "<", ">"),
                ast.ignore(None, "<", [">", ">"]),
            ],
        ),
        ast.subst_liga(
            "</",
            banner=[
                ast.ignore("<", "<", "/"),
                ast.ignore(None, "<", ["/", ast.cls("/", ">")]),
            ],
        ),
        ast.subst_liga(
            "/>",
            banner=[
                ast.ignore(ast.cls("<", "/"), "/", ">"),
                ast.ignore(None, "/", [">", ">"]),
            ],
        ),
        ast.subst_liga(
            "</>",
            banner=[
                ast.ignore(["<", "<"], "/", ">"),
                ast.ignore(None, "<", ["/", ">", ">"]),
            ],
        ),
        ast.subst_liga(
            "<+",
            banner=[
                ast.ignore("<", "<", "+"),
                ast.ignore(None, "<", ["+", ast.cls("+", ">")]),
            ],
        ),
        ast.subst_liga(
            "+>",
            banner=[
                ast.ignore(ast.cls("+", "<"), "+", ">"),
                ast.ignore(None, "+", [">", ">"]),
            ],
        ),
        ast.subst_liga(
            "<+>",
            banner=[
                ast.ignore(["<", "<"], "+", ">"),
                ast.ignore(None, "<", ["+", ">", ">"]),
            ],
        ),
        ast.subst_liga(
            "<*",
            banner=[
                ast.ignore("<", "<", "*"),
                ast.ignore(None, "<", ["*", ast.cls("*", ">")]),
            ],
        ),
        ast.subst_liga(
            "*>",
            banner=[
                ast.ignore(ast.cls("*", "<"), "*", ">"),
                ast.ignore(None, "*", [">", ">"]),
            ],
        ),
        ast.subst_liga(
            "<*>",
            banner=[
                ast.ignore(["<", "<"], "*", ">"),
                ast.ignore(None, "<", ["*", ">", ">"]),
            ],
        ),
    ]
