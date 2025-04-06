from source.py.feature import ast


def ss08_subst():
    return [
        # --------------------------------------------------------------------
        ast.subst_liga(
            "<<-",
            target=ast.gly("<<-", ".ss08", True),
            banner=[
                ast.ignore("<", "<", ["<", "-"]),
                ast.ignore(None, "<", ["<", "-", "-"]),
                ast.subst(ast.SPC, ast.gly("<<"), "-", ast.SPC),
            ],
        ),
        # --------------------------------------------------------------------
        ast.subst_liga(
            ">>-",
            target=ast.gly(">>-", ".ss08", True),
            banner=[
                ast.ignore(">", ">", [">", "-"]),
                ast.ignore(None, ">", [">", "-", "-"]),
                ast.subst(ast.SPC, ast.gly(">>"), "-", ast.SPC),
            ],
        ),
        # --------------------------------------------------------------------
        ast.subst_liga(
            "<<=",
            target=ast.gly("<<=", ".ss08", True),
            banner=[
                ast.ignore("<", "<", ["<", "="]),
                ast.ignore(None, "<", ["<", "=", "="]),
                ast.subst(ast.SPC, ast.gly("<<"), "=", ast.SPC),
            ],
        ),
        # --------------------------------------------------------------------
        ast.subst_liga(
            ">>=",
            target=ast.gly(">>=", ".ss08", True),
            banner=[
                ast.ignore(">", ">", [">", "="]),
                ast.ignore(None, ">", [">", "=", "="]),
                ast.subst(ast.SPC, ast.gly(">>"), "=", ast.SPC),
            ],
        ),
        # --------------------------------------------------------------------
        ast.subst_liga(
            "-<<",
            target=ast.gly("-<<", ".ss08", True),
            banner=[
                ast.ignore("-", "-", ["<", "<"]),
                ast.ignore(None, "-", ["<", "<", "<"]),
                ast.subst(
                    [ast.SPC, ast.SPC],
                    ast.gly("<<"),
                    None,
                    ast.gly("-<<", ".ss08", True),
                ),
                ast.subst(None, "-", [ast.SPC, ast.gly("<<")], ast.SPC),
            ],
        ),
        # --------------------------------------------------------------------
        ast.subst_liga(
            "->>",
            target=ast.gly("->>", ".ss08", True),
            banner=[
                ast.ignore("-", "-", [">", ">"]),
                ast.ignore(None, "-", [">", ">", ">"]),
                ast.subst(
                    [ast.SPC, ast.SPC],
                    ast.gly(">>"),
                    None,
                    ast.gly("->>", ".ss08", True),
                ),
                ast.subst(None, "-", [ast.SPC, ast.gly(">>")], ast.SPC),
            ],
        ),
        # --------------------------------------------------------------------
        ast.subst_liga(
            "=<<",
            target=ast.gly("=<<", ".ss08", True),
            banner=[
                ast.ignore("=", "=", ["<", "<"]),
                ast.ignore(["(", "?"], "=", ["<", "<"]),
                ast.ignore(None, "=", ["<", "<", "<"]),
                ast.subst(
                    [ast.SPC, ast.SPC],
                    ast.gly("<<"),
                    None,
                    ast.gly("=<<", ".ss08", True),
                ),
                ast.subst(None, "=", [ast.SPC, ast.gly("<<")], ast.SPC),
            ],
        ),
        # --------------------------------------------------------------------
        ast.subst_liga(
            "=>>",
            target=ast.gly("=>>", ".ss08", True),
            banner=[
                ast.ignore("=", "=", [">", ">"]),
                ast.ignore(["(", "?"], "=", [">", ">"]),
                ast.ignore(None, "=", [">", ">", ">"]),
                ast.subst(
                    [ast.SPC, ast.SPC],
                    ast.gly(">>"),
                    None,
                    ast.gly("=>>", ".ss08", True),
                ),
                ast.subst(None, "=", [ast.SPC, ast.gly(">>")], ast.SPC),
            ],
        ),
        # --------------------------------------------------------------------
        ast.subst_liga(
            "-<",
            target=ast.gly("-<", ".ss08", True),
            banner=[
                ast.ignore(ast.clazz([">", "<", "-"]), "-", "<"),
                ast.ignore(None, "-", ["<", ast.clazz(["<", "/", "?"])]),
            ],
        ),
        # --------------------------------------------------------------------
        ast.subst_liga(
            ">-",
            target=ast.gly(">-", ".ss08", True),
            banner=[
                ast.ignore(">", ">", "-"),
                ast.ignore(None, ">", ["-", ast.clazz(["-", ">", "<"])]),
            ],
        ),
        # --------------------------------------------------------------------
    ]


ss08_name = "Double headed arrows and reverse arrows ligatures"
ss08_feat = ast.ss(8, ss08_name, ss08_subst())
