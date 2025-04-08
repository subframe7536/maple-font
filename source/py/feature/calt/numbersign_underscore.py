from source.py.feature import ast


start = "numbersign_start.liga"
mid = "numbersign_middle.liga"
end = "numbersign_end.liga"


def get_lookup():
    return [
        ast.subst_liga(
            "__",
            banner=[
                ast.ignore(ast.clazz(["_", "#"]), "_", "_"),
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
                ast.ignore(None, "#", ["!", "!"]),
            ],
        ),
        ast.subst_liga(
            "#:",
            banner=[
                ast.ignore("#", "#", ":"),
                ast.ignore(None, "#", [":", ":"]),
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
                ast.ignore(None, "#", ["_", ast.clazz(["_", "("])]),
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
        ast.lookup(
            "numbersigns",
            "Infinity #",
            [
                ast.subst(ast.clazz([start, mid]), "#", "#", mid),
                ast.subst(ast.clazz([start, mid]), "#", None, end),
                ast.subst(None, "#", "#", start),
            ],
        ),
    ]
