from source.py.feature import ast


def ss11_subst():
    cls_ign_equal = ast.Clazz("IgnoreEqual", [">", "=", ":"])
    ampersand_cv01 = ast.gly("&", ".cv01")
    question_cv62 = ast.gly("?", ".cv62")
    ampersand_cv65 = ast.gly("&", ".cv65")
    return [
        ast.cls_states(cls_ign_equal),
        ast.Lookup(
            "bars_equal",
            "|=",
            ast.subst_map(["|="], target_suffix=".ss11"),
        ),
        ast.subst_liga(
            "||=",
            target=ast.gly("||=", ".ss11"),
            ign_prefix="|",
            ign_suffix="|",
            extra_rules=[ast.subst(ast.SPC, ast.gly("||"), "=", ast.SPC)],
        ),
        ast.subst_liga(
            "/=",
            target=ast.gly("/=", ".ss11"),
            ign_prefix=ast.cls("/", "<"),
            ign_suffix=cls_ign_equal,
        ),
        ast.subst_liga(
            "//=",
            target=ast.gly("//=", ".ss11"),
            ign_prefix=ast.cls("/", "<"),
            ign_suffix=cls_ign_equal,
            extra_rules=[ast.subst(ast.SPC, ast.gly("//"), "=", ast.SPC)],
        ),
        ast.subst_liga(
            "^=",
            target=ast.gly("^=", ".ss11"),
            ign_prefix="^",
            ign_suffix=cls_ign_equal,
        ),
        ast.subst_liga(
            "&=",
            target=ast.gly("&=", ".ss11"),
            ign_prefix="&",
            ign_suffix=cls_ign_equal,
        ),
        ast.subst_liga(
            [ampersand_cv01, "="],
            target=ast.gly("&=", ".cv01.ss11"),
            desc="&= in cv01",
            ign_prefix=ampersand_cv01,
            ign_suffix=cls_ign_equal,
        ),
        ast.subst_liga(
            [ampersand_cv65, "="],
            target=ast.gly("&=", ".cv65.ss11"),
            desc="&= in cv65",
            ign_prefix=ampersand_cv65,
            ign_suffix=cls_ign_equal,
        ),
        ast.subst_liga(
            "&&=",
            target=ast.gly("&&=", ".ss11"),
            ign_prefix="&",
            ign_suffix=cls_ign_equal,
            extra_rules=[ast.subst(ast.SPC, ast.gly("&&"), "=", ast.SPC)],
        ),
        ast.subst_liga(
            [ampersand_cv01, ampersand_cv01, "="],
            target=ast.gly("&&=", ".cv01.ss11"),
            desc="&&= in cv01",
            ign_prefix=ampersand_cv01,
            ign_suffix=cls_ign_equal,
            extra_rules=[
                ast.subst(
                    ast.SPC,
                    ast.gly("&&", ".cv01"),
                    "=",
                    ast.SPC,
                )
            ],
        ),
        ast.subst_liga(
            [ampersand_cv65, ampersand_cv65, "="],
            target=ast.gly("&&=", ".cv65.ss11"),
            desc="&&= in cv65",
            ign_prefix=ampersand_cv65,
            ign_suffix=cls_ign_equal,
            extra_rules=[
                ast.subst(
                    ast.SPC,
                    ast.gly("&&", ".cv65"),
                    "=",
                    ast.SPC,
                )
            ],
        ),
        ast.subst_liga(
            "?=",
            target=ast.gly("?=", ".ss11"),
            ign_prefix="?",
            ign_suffix=cls_ign_equal,
        ),
        ast.subst_liga(
            [question_cv62, "="],
            target=ast.gly("?=", ".cv62.ss11"),
            desc="?= in cv62",
            ign_prefix=question_cv62,
            ign_suffix=cls_ign_equal,
        ),
        ast.subst_liga(
            "??=",
            target=ast.gly("??=", ".ss11"),
            ign_prefix="?",
            ign_suffix=cls_ign_equal,
            extra_rules=[ast.subst(ast.SPC, ast.gly("??"), "=", ast.SPC)],
        ),
        ast.subst_liga(
            [question_cv62, question_cv62, "="],
            target=ast.gly("??=", ".cv62.ss11"),
            desc="??= in cv62",
            ign_prefix=question_cv62,
            ign_suffix=cls_ign_equal,
            extra_rules=[ast.subst(ast.SPC, ast.gly("??", ".cv62"), "=", ast.SPC)],
        ),
    ]


ss11_name = "Equal and extra punctuation ligatures (`|=`, `/=`, `?=`, `&=`, ...)"
ss11_feat = ast.StylisticSet(
    id=11, desc=ss11_name, content=ss11_subst(), version="7.1", example="|="
)
