from source.py.feature import ast


def get_lookup():
    return [
        ast.subst_liga("Cl", ign_suffix="l"),
        ast.subst_liga("al", ign_suffix="l"),
        ast.subst_liga("cl", ign_suffix="l"),
        ast.subst_liga("el", ign_suffix="l"),
        ast.subst_liga("il", ign_suffix="l"),
        ast.subst_liga("tl", ign_suffix="l"),
        ast.subst_liga("ul", ign_suffix="l"),
        ast.subst_liga("xl", ign_suffix="l"),
        ast.subst_liga("ff", ign_prefix="f", ign_suffix="f"),
        ast.subst_liga("tt", ign_prefix="t", ign_suffix=ast.cls("t", "l")),
        ast.subst_liga("all", ign_suffix="l"),
        ast.subst_liga("ell", ign_suffix="l"),
        ast.subst_liga("ill", ign_suffix="l"),
        ast.subst_liga("ull", ign_suffix="l"),
        ast.subst_liga(
            "ll",
            ign_prefix=ast.cls(
                "C",
                "a",
                "c",
                "e",
                "i",
                "t",
                "u",
                "x",
            ),
            ign_suffix="l",
        ),
    ]
