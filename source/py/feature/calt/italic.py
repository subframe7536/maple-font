from source.py.feature import ast


def get_lookup():
    return [
        ast.subst_liga("Cl", desc="italic Cl", ign_suffix="l"),
        ast.subst_liga("al", desc="italic al", ign_suffix="l"),
        ast.subst_liga("cl", desc="italic cl", ign_suffix="l"),
        ast.subst_liga("el", desc="italic el", ign_suffix="l"),
        ast.subst_liga("il", desc="italic il", ign_suffix="l"),
        ast.subst_liga("tl", desc="italic tl", ign_suffix="l"),
        ast.subst_liga("ul", desc="italic ul", ign_suffix="l"),
        ast.subst_liga("xl", desc="italic xl", ign_suffix="l"),
        ast.subst_liga("ff", desc="italic ff", ign_prefix="f", ign_suffix="f"),
        ast.subst_liga(
            "tt", desc="italic tt", ign_prefix="t", ign_suffix=ast.cls("t", "l")
        ),
        ast.subst_liga("all", desc="italic all", ign_suffix="l"),
        ast.subst_liga("ell", desc="italic ell", ign_suffix="l"),
        ast.subst_liga("ill", desc="italic ill", ign_suffix="l"),
        ast.subst_liga("ull", desc="italic ull", ign_suffix="l"),
        ast.subst_liga(
            "ll",
            desc="italic ll",
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
