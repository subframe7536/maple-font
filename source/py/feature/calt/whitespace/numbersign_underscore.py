from source.py.feature import ast


start = "numbersign_start.liga"
mid = "numbersign_middle.liga"
end = "numbersign_end.liga"


def get_lookup():
    return [
        ast.subst_liga(
            "__",
            banner=[
                ast.ignore(ast.cls("_", "#"), "_", "_"),
                ast.ignore(None, "_", ["_", "_"]),
            ],
        ),
        ast.subst_liga(
            "#{",
            banner=[
                ast.ignore("#", "#", "{"),
                ast.ignore(None, "#", ["{", "{"]),
            ],
        ),
        ast.subst_liga(
            "#[",
            banner=[
                ast.ignore("#", "#", "["),
                ast.ignore(None, "#", ["[", "["]),
            ],
        ),
        ast.subst_liga(
            "#(",
            banner=[
                ast.ignore("#", "#", "("),
                ast.ignore(None, "#", ["(", "("]),
            ],
        ),
        ast.subst_liga(
            "#?",
            banner=[
                ast.ignore("#", "#", "?"),
                ast.ignore(None, "#", ["?", "?"]),
            ],
        ),
        ast.subst_liga(
            "#!",
            banner=[
                ast.ignore("#", "#", "!"),
                ast.ignore(None, "#", ["!", ast.cls("!", "=")]),
            ],
        ),
        ast.subst_liga(
            "#:",
            banner=[
                ast.ignore("#", "#", ":"),
                ast.ignore(None, "#", [":", ast.cls(":", "=")]),
            ],
        ),
        ast.subst_liga(
            "#=",
            banner=[
                ast.ignore("#", "#", "="),
                ast.ignore(None, "#", ["=", "="]),
            ],
        ),
        ast.subst_liga(
            "#_",
            banner=[
                ast.ignore("#", "#", "_"),
                ast.ignore(None, "#", ["_", ast.cls("_", "(")]),
            ],
        ),
        ast.subst_liga(
            "#__",
            banner=[
                ast.ignore(None, "#", ["_", "_", "_"]),
            ],
        ),
        ast.subst_liga(
            "#_(",
            banner=[
                ast.ignore(None, "#", ["_", "(", "("]),
            ],
        ),
        ast.subst_liga(
            "]#",
            banner=[
                ast.ignore("]", "]", "#"),
                ast.ignore(None, "]", ["#", "#"]),
            ],
        ),
        ast.Lookup(
            "infinity_numbersigns",
            "#######",
            [
                ast.subst(ast.cls(start, mid), "#", "#", mid),
                ast.subst(ast.cls(start, mid), "#", None, end),
                ast.subst(None, "#", "#", start),
            ],
        ),
    ]
