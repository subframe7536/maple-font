from source.py.feature import ast
from source.py.feature.base.clazz import cls_question


def get_lookup():
    cls_ign_colon = ast.Clazz("IgnoreColon", ["<", ":", ">", "="])
    cls_ign_markup = ast.Clazz("IgnoreMarkup", ["<", "/", ">"])

    return [
        ast.subst_liga(
            "::",
            banner=[
                ast.ignore(":", ":", ":"),
                ast.ignore(None, ":", [":", ast.cls("=", ":")]),
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
            [cls_question.use(), ast.gly(":")],
            target=ast.gly("?:"),
            desc="?:",
            banner=[
                ast.ignore(cls_question, cls_question, ":"),
                ast.ignore(None, cls_question, [":", ast.cls(":", "=")]),
            ],
        ),
        ast.subst_liga(
            [ast.gly(":"), cls_question.use()],
            target=ast.gly(":?"),
            desc=":?",
            banner=[
                ast.ignore(":", ":", cls_question),
                ast.ignore(None, ":", [cls_question, ast.cls(cls_question, ">")]),
            ],
        ),
        ast.subst_liga(
            [ast.gly(":"), cls_question.use(), ast.gly(">")],
            target=ast.gly(":?>"),
            desc=":?>",
            banner=[
                ast.ignore(":", ":", [cls_question, ">"]),
                ast.ignore(None, ":", [cls_question, ">", ">"]),
            ],
        ),
        ast.cls_states(
            cls_ign_colon,
            cls_ign_markup,
        ),
        ast.subst_liga(
            ":=",
            banner=[
                ast.ignore(ast.cls(cls_ign_colon, cls_question), ":", "="),
                ast.ignore(None, ":", ["=", ast.cls("=", ":")]),
            ],
        ),
        ast.subst_liga(
            "=:",
            banner=[
                ast.ignore(cls_ign_colon, "=", ":"),
                ast.ignore(["(", cls_question], "=", ":"),
                ast.ignore(None, "=", [":", ast.cls("=", ":")]),
            ],
        ),
        ast.subst_liga(
            ":=:",
            banner=[
                ast.ignore(ast.cls(cls_ign_colon, cls_question), ":", ["=", ":"]),
                ast.ignore(["(", cls_question], ":", ["=", ":"]),
                ast.ignore(None, ":", ["=", ":", ast.cls(cls_ign_colon, cls_question)]),
            ],
        ),
        ast.subst_liga(
            "=:=",
            banner=[
                ast.ignore("=", "=", [":", "="]),
                ast.ignore(None, "=", [":", "=", "="]),
                ast.ignore(["(", cls_question], "=", [":", "="]),
            ],
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
