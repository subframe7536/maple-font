from source.py.feature import ast


def ss11_subst():
    cls_ign_equal = ast.Clazz("IgnoreEqual", [">", "=", ":"])
    g_cv01 = ast.gly("&", ".cv01")
    g_cv62 = ast.gly("?", ".cv62")
    return [
        ast.cls_states(cls_ign_equal),
        ast.subst_map(["|=", "||="], target_suffix=".ss11"),
        ast.subst_liga(
            "/=",
            target=ast.gly("/=", ".ss11"),
            banner=[
                ast.ignore(ast.cls("/", "<"), "/", "="),
                ast.ignore(None, "/", ["=", cls_ign_equal]),
            ],
        ),
        ast.subst_liga(
            "//=",
            target=ast.gly("//=", ".ss11"),
            banner=[
                ast.ignore(ast.cls("/", "<"), "/", ["/", "="]),
                ast.ignore(None, "/", ["/", "=", cls_ign_equal]),
            ],
        ),
        ast.subst_liga(
            "^=",
            target=ast.gly("^=", ".ss11"),
            banner=[
                ast.ignore("^", "^", "="),
                ast.ignore(None, "^", ["=", cls_ign_equal]),
            ],
        ),
        ast.subst_liga(
            "&=",
            target=ast.gly("&=", ".ss11"),
            banner=[
                ast.ignore("&", "&", "="),
                ast.ignore(None, "&", ["=", cls_ign_equal]),
            ],
        ),
        ast.subst_liga(
            [g_cv01, "="],
            target=ast.gly("&=", ".cv01.ss11"),
            banner=[
                ast.ignore(g_cv01, g_cv01, "="),
                ast.ignore(None, g_cv01, ["=", cls_ign_equal]),
            ],
        ),
        ast.subst_liga(
            "&&=",
            target=ast.gly("&&=", ".ss11"),
            banner=[
                ast.ignore("&", "&", ["&", "="]),
                ast.ignore(None, "&", ["&", "=", cls_ign_equal]),
            ],
        ),
        ast.subst_liga(
            [g_cv01, g_cv01,"="],
            target=ast.gly("&&=", ".cv01.ss11"),
            banner=[
                ast.ignore(g_cv01, g_cv01, [g_cv01, "="]),
                ast.ignore(None, g_cv01, [g_cv01, "=", cls_ign_equal]),
            ],
        ),
        ast.subst_liga(
            "?=",
            target=ast.gly("?=", ".ss11"),
            banner=[
                ast.ignore("?", "?", "="),
                ast.ignore(None, "?", ["=", cls_ign_equal]),
            ],
        ),
        ast.subst_liga(
            [g_cv62,"="],
            target=ast.gly("?=", ".cv62.ss11"),
            banner=[
                ast.ignore(g_cv62, g_cv62, "="),
                ast.ignore(None, g_cv62, ["=", cls_ign_equal]),
            ],
        ),
        ast.subst_liga(
            "??=",
            target=ast.gly("??=", ".ss11"),
            banner=[
                ast.ignore("?", "?", ["?", "="]),
                ast.ignore(None, "?", ["?", "=", cls_ign_equal]),
            ],
        ),
        ast.subst_liga(
            [g_cv62, g_cv62,"="],
            target=ast.gly("??=", ".cv62.ss11"),
            banner=[
                ast.ignore(g_cv62, g_cv62, [g_cv62, "="]),
                ast.ignore(None, g_cv62, [g_cv62, "=", cls_ign_equal]),
            ],
        ),
    ]


ss11_name = "Equal and extra punctuation ligatures (`|=`, `/=`, `?=`, `&=`, ...)"
ss11_feat = ast.StylisticSet(11, ss11_name, ss11_subst())
