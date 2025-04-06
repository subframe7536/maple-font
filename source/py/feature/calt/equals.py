from source.py.feature import ast


def get_lookup():
    return [
        ast.subst_liga(
            "==",
            banner=[
                ast.ignore("=", "=", "="),
                ast.ignore(None, "=", ["=", ast.clazz(["=", ">"])]),
                ast.ignore(["(", "?"], "=", "="),
                ast.ignore(["(", "?", "<"], "=", "="),
            ],
        ),
        ast.subst_liga(
            "===",
            banner=[
                ast.ignore("=", "=", ["=", "="]),
                ast.ignore(None, "=", ["=", "=", ast.clazz(["=", ">"])]),
                ast.ignore(["(", "?"], "=", ["=", "="]),
                ast.ignore(["(", "?", "<"], "=", ["=", "="]),
            ],
        ),
        ast.subst_liga(
            "!=",
            banner=[
                ast.ignore(ast.clazz(["!", "="]), "!", "="),
                ast.ignore(None, "!", ["=", "="]),
                ast.ignore(["(", "?"], "!", "="),
                ast.ignore(["(", "?", "<"], "!", "="),
            ],
        ),
        ast.subst_liga(
            "!==",
            banner=[
                ast.ignore(ast.clazz(["!", "="]), "!", ["=", "="]),
                ast.ignore(None, "!", ["=", "=", "="]),
                ast.ignore(["(", "?"], "!", ["=", "="]),
                ast.ignore(["(", "?", "<"], "!", ["=", "="]),
            ],
        ),
        ast.subst_liga(
            "=/=",
            banner=[
                ast.ignore("=", "=", ["/", "="]),
                ast.ignore(None, "=", ["/", "=", "="]),
                ast.ignore(["(", "?"], "=", ["/", "="]),
                ast.ignore(["(", "?", "<"], "=", ["/", "="]),
            ],
        ),
        ast.subst_liga(
            "=!=",
            banner=[
                ast.ignore("=", "=", ["!", "="]),
                ast.ignore(None, "=", ["!", "=", "="]),
                ast.ignore(["(", "?"], "=", ["!", "="]),
                ast.ignore(["(", "?", "<"], "=", ["!", "="]),
            ],
        ),
        ast.subst_liga(
            "=<=",
            banner=[
                ast.ignore(ast.clazz(["=", ">", "<", "|"]), "=", ["<", "="]),
                ast.ignore(None, "=", ["<", "=", ast.clazz(["=", "<", ">"])]),
                ast.ignore(["(", "?"], "=", [">", "="]),
            ],
        ),
        ast.subst_liga(
            "=>=",
            banner=[
                ast.ignore(ast.clazz(["=", ">", "<", "|"]), "=", [">", "="]),
                ast.ignore(None, "=", [">", "=", ast.clazz(["=", "<", ">"])]),
                ast.ignore(["(", "?"], "=", [">", "="]),
            ],
        ),
        ast.subst_liga(
            "|=",
            banner=[
                ast.ignore("|", "|", "="),
                ast.ignore(None, "|", ["=", ast.clazz([">", "="])]),
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
