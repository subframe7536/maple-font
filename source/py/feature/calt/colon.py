from source.py.feature import ast


def get_lookup():
    cls_ign_colon = ast.Clazz("IgnoreColon", ["<", ":", ">"])
    cls_ign_markup = ast.Clazz("IgnoreMarkup", ["<", "/", ">"])

    return [
        ast.subst_liga(
            "::",
            banner=[
                ast.ignore(":", ":", ":"),
                ast.ignore(None, ":", [":", ast.clazz(["=", ":"])]),
            ],
        ),
        ast.subst_liga(
            ":::",
            banner=[
                ast.ignore(":", ":", [":", ":"]),
                ast.ignore(None, ":", [":", ":", ":"]),
            ],
        ),
        ast.subst_liga(
            ":?",
            banner=[
                ast.ignore(":", ":", "?"),
                ast.ignore(None, ":", ["?", ast.clazz(["?", ">"])]),
            ],
        ),
        ast.subst_liga(
            ":?>",
            banner=[
                ast.ignore(":", ":", ["?", ">"]),
                ast.ignore(None, ":", ["?", ">", ">"]),
            ],
        ),
        ast.subst_liga(
            ":=",
            banner=[
                ast.ignore(ast.clazz(["=", ":"]), ":", "="),
                ast.ignore(None, ":", ["=", ast.clazz(["=", ":"])]),
            ],
        ),
        ast.subst_liga(
            "=:",
            banner=[
                ast.ignore(ast.clazz(["=", ":"]), "=", ":"),
                ast.ignore(None, "=", [":", ast.clazz(["=", ":"])]),
            ],
        ),
        ast.subst_liga(
            ":=:",
            banner=[
                ast.ignore(ast.clazz(["=", ":", "<", ">", "?"]), ":", ["=", ":"]),
                ast.ignore(None, ":", ["=", ":", ast.clazz(["=", ":", "<", ">", "?"])]),
            ],
        ),
        ast.subst_liga(
            "=:=",
            banner=[
                ast.ignore("=", "=", [":", "="]),
                ast.ignore(None, "=", [":", "=", "="]),
                ast.ignore(["(", "?"], "=", [":", "="]),
            ],
        ),
        ast.clazz_states(
            [
                cls_ign_colon,
                cls_ign_markup,
            ]
        ),
        ast.subst_liga(
            "<:",
            banner=[
                ast.ignore("<", "<", ":"),
                ast.ignore(None, "<", [":", cls_ign_colon]),
            ],
        ),
        ast.subst_liga(
            ":>",
            banner=[
                ast.ignore(cls_ign_colon, ":", ">"),
                ast.ignore(None, ":", [">", ">"]),
            ],
        ),
        ast.subst_liga(
            ":<",
            banner=[
                ast.ignore(cls_ign_colon, ":", "<"),
                ast.ignore(None, ":", ["<", cls_ign_markup]),
            ],
        ),
        ast.subst_liga(
            "<:<",  # scala / haskell
            banner=[
                ast.ignore("<", "<", [":", "<"]),
                ast.ignore(None, "<", [":", "<", cls_ign_markup]),
            ],
        ),
        ast.subst_liga(
            ">:>",  # scala / haskell
            banner=[
                ast.ignore(cls_ign_markup, ">", [":", ">"]),
                ast.ignore(None, ">", [":", ">", ">"]),
            ],
        ),
        ast.subst_liga(
            "::=",
            banner=[
                ast.ignore(":", ":", [":", "="]),
                ast.ignore(None, ":", [":", "=", "="]),
            ],
        ),
    ]
