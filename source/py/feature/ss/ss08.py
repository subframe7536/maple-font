from source.py.feature import ast
from source.py.feature.base.clazz import cls_question

def ss08_subst():
    return [
        ast.subst_liga(
            "<<-",
            target=ast.gly("<<-", ".ss08"),
            banner=[
                ast.ignore("<", "<", ["<", "-"]),
                ast.ignore(None, "<", ["<", "-", "-"]),
                ast.subst(ast.SPC, ast.gly("<<"), "-", ast.SPC),
            ],
        ),
        ast.subst_liga(
            ">>-",
            target=ast.gly(">>-", ".ss08"),
            banner=[
                ast.ignore(">", ">", [">", "-"]),
                ast.ignore(None, ">", [">", "-", "-"]),
                ast.subst(ast.SPC, ast.gly(">>"), "-", ast.SPC),
            ],
        ),
        ast.subst_liga(
            "<<=",
            target=ast.gly("<<=", ".ss08"),
            banner=[
                ast.ignore("<", "<", ["<", "="]),
                ast.ignore(None, "<", ["<", "=", "="]),
                ast.subst(ast.SPC, ast.gly("<<"), "=", ast.SPC),
            ],
        ),
        ast.subst_liga(
            ">>=",
            target=ast.gly(">>=", ".ss08"),
            banner=[
                ast.ignore(">", ">", [">", "="]),
                ast.ignore(None, ">", [">", "=", "="]),
                ast.subst(ast.SPC, ast.gly(">>"), "=", ast.SPC),
            ],
        ),
        ast.subst_liga(
            "-<<",
            target=ast.gly("-<<", ".ss08"),
            banner=[
                ast.ignore("-", "-", ["<", "<"]),
                ast.ignore(None, "-", ["<", "<", "<"]),
                ast.subst(
                    [ast.SPC, ast.SPC],
                    ast.gly("<<"),
                    None,
                    ast.gly("-<<", ".ss08"),
                ),
                ast.subst(None, "-", [ast.SPC, ast.gly("<<")], ast.SPC),
            ],
        ),
        ast.subst_liga(
            "->>",
            target=ast.gly("->>", ".ss08"),
            banner=[
                ast.ignore("-", "-", [">", ">"]),
                ast.ignore(None, "-", [">", ">", ">"]),
                ast.subst(
                    [ast.SPC, ast.SPC],
                    ast.gly(">>"),
                    None,
                    ast.gly("->>", ".ss08"),
                ),
                ast.subst(None, "-", [ast.SPC, ast.gly(">>")], ast.SPC),
            ],
        ),
        ast.subst_liga(
            "=<<",
            target=ast.gly("=<<", ".ss08"),
            banner=[
                ast.ignore("=", "=", ["<", "<"]),
                ast.ignore(["(", cls_question], "=", ["<", "<"]),
                ast.ignore(None, "=", ["<", "<", "<"]),
                ast.subst(
                    [ast.SPC, ast.SPC],
                    ast.gly("<<"),
                    None,
                    ast.gly("=<<", ".ss08"),
                ),
                ast.subst(None, "=", [ast.SPC, ast.gly("<<")], ast.SPC),
            ],
        ),
        ast.subst_liga(
            "=>>",
            target=ast.gly("=>>", ".ss08"),
            banner=[
                ast.ignore("=", "=", [">", ">"]),
                ast.ignore(["(", cls_question], "=", [">", ">"]),
                ast.ignore(None, "=", [">", ">", ">"]),
                ast.subst(
                    [ast.SPC, ast.SPC],
                    ast.gly(">>"),
                    None,
                    ast.gly("=>>", ".ss08"),
                ),
                ast.subst(None, "=", [ast.SPC, ast.gly(">>")], ast.SPC),
            ],
        ),
        ast.subst_liga(
            "-<",
            target=ast.gly("-<", ".ss08"),
            banner=[
                ast.ignore(ast.cls(">", "<", "-"), "-", "<"),
                ast.ignore(None, "-", ["<", ast.cls("<", "/", cls_question)]),
            ],
        ),
        ast.subst_liga(
            ">-",
            target=ast.gly(">-", ".ss08"),
            banner=[
                ast.ignore(">", ">", "-"),
                ast.ignore(None, ">", ["-", ast.cls("-", ">", "<")]),
            ],
        ),
    ]


ss08_name = (
    "Double headed arrows and reverse arrows ligatures (`>>=`, `-<<`, `->>`, `>-` ...)"
)
ss08_feat = ast.StylisticSet(8, ss08_name, ss08_subst())
