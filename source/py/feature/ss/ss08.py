from source.py.feature import ast
from source.py.feature.base.clazz import cls_question


def ss08_subst():
    return [
        ast.subst_liga(
            "<<-",
            target=ast.gly("<<-", ".ss08"),
            ign_prefix=ast.cls("<", "-"),
            ign_suffix=ast.cls("<", ">", "-"),
            extra_rules=[
                ast.subst(ast.SPC, ast.gly("<<"), "-", ast.SPC),
            ],
        ),
        ast.subst_liga(
            ">>-",
            target=ast.gly(">>-", ".ss08"),
            ign_prefix=ast.cls(">", "-"),
            ign_suffix=ast.cls("-", ">", "<"),
            extra_rules=[
                ast.subst(ast.SPC, ast.gly(">>"), "-", ast.SPC),
            ],
        ),
        ast.subst_liga(
            "<<=",
            target=ast.gly("<<=", ".ss08"),
            ign_prefix=ast.cls("=", "<"),
            ign_suffix=ast.cls("=", ">", "<"),
            extra_rules=[
                ast.subst(ast.SPC, ast.gly("<<"), "=", ast.SPC),
            ],
        ),
        ast.subst_liga(
            ">>=",
            target=ast.gly(">>=", ".ss08"),
            ign_prefix=ast.cls(">", "="),
            ign_suffix=ast.cls("=", ">", "<"),
            extra_rules=[
                ast.subst(ast.SPC, ast.gly(">>"), "=", ast.SPC),
            ],
        ),
        ast.subst_liga(
            "-<<",
            target=ast.gly("-<<", ".ss08"),
            ign_prefix=ast.cls("-", "<", ">"),
            ign_suffix=ast.cls("<", "-"),
            extra_rules=[
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
            ign_prefix=ast.cls("-", ">", "<"),
            ign_suffix=ast.cls(">", "-"),
            extra_rules=[
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
            ign_prefix=ast.cls("=", "<", ">"),
            ign_suffix=ast.cls("<", "="),
            extra_rules=[
                ast.ign(["(", cls_question], "=", ["<", "<"]),
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
            ign_prefix=ast.cls("=", ">", "<"),
            ign_suffix=ast.cls(">", "="),
            extra_rules=[
                ast.ign(["(", cls_question], "=", [">", ">"]),
                ast.subst(
                    [ast.SPC, ast.SPC],
                    ast.gly(">>"),
                    None,
                    ast.gly("=>>", ".ss08"),
                ),
                ast.subst(None, "=", [ast.SPC, ast.gly(">>")], ast.SPC),
            ],
        ),
    ]


ss08_name = (
    "Double headed arrows and reverse arrows ligatures (`>>=`, `-<<`, `->>`, `>>-` ...)"
)
ss08_feat = ast.StylisticSet(
    id=8, desc=ss08_name, content=ss08_subst(), version="7.0", example=">>="
)
