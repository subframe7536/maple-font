from source.py.feature import ast


def get_lookup():
    return [
        ast.subst_liga("Cl", banner=[ast.ignore(None, "C", ["l", "l"])]),
        ast.subst_liga("al", banner=[ast.ignore(None, "a", ["l", "l"])]),
        ast.subst_liga("cl", banner=[ast.ignore(None, "c", ["l", "l"])]),
        ast.subst_liga("el", banner=[ast.ignore(None, "e", ["l", "l"])]),
        ast.subst_liga("il", banner=[ast.ignore(None, "i", ["l", "l"])]),
        ast.subst_liga("tl", banner=[ast.ignore(None, "l", ["l", "l"])]),
        ast.subst_liga("ul", banner=[ast.ignore(None, "u", ["l", "l"])]),
        ast.subst_liga("xl", banner=[ast.ignore(None, "x", ["l", "l"])]),
        ast.subst_liga("ff", banner=[ast.ignore(None, "f", ["f", "f"])]),
        ast.subst_liga("tt", banner=[ast.ignore(None, "t", ["t", "t"])]),
        ast.subst_liga("all", banner=[ast.ignore(None, "a", ["l", "l", "l"])]),
        ast.subst_liga("ell", banner=[ast.ignore(None, "e", ["l", "l", "l"])]),
        ast.subst_liga("ill", banner=[ast.ignore(None, "i", ["l", "l", "l"])]),
        ast.subst_liga("ull", banner=[ast.ignore(None, "u", ["l", "l", "l"])]),
        ast.subst_liga(
            "ll",
            banner=[
                ast.ignore(
                    ast.cls(
                        [
                            "C",
                            "a",
                            "c",
                            "e",
                            "i",
                            "t",
                            "u",
                            "x",
                        ]
                    ),
                    "l",
                    "l",
                ),
                ast.ignore(None, "l", ["l", "l"]),
            ],
        ),
    ]
