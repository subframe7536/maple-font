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
                ast.ignore(None, "#", ["_", "_"]),
            ],
        ),
        ast.subst_liga(
            "#__",
            banner=[
                ast.ignore("#", "#", ["_", "_"]),
                ast.ignore(None, "#", ["_", "_", "_"]),
            ],
        ),
        ast.lookup(
            ast.gly("##__"),
            "##__",
            [
                ast.ignore("#", "#", [ast.SPC, ast.SPC, ast.gly("#__")]),
                ast.subst(None, "#", [ast.SPC, ast.SPC, ast.gly("#__")], start),
            ],
        ),
        ast.subst_liga(
            "#_(",
            banner=[
                ast.ignore("#", "#", ["_", "("]),
                ast.ignore(None, "#", ["_", "(", "("]),
            ],
        ),
        ast.lookup(
            ast.gly("##_("),
            "##_(",
            [
                ast.ignore("#", "#", [ast.SPC, ast.SPC, ast.gly("#_(")]),
                ast.subst(None, "#", [ast.SPC, ast.SPC, ast.gly("#_(")], start),
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
