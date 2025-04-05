from source.py.feature import ast
from source.py.feature.shared.clazz import digit


def get_lookup(letter_list: list[ast.Clazz]):
    var = ast.Clazz("Var", ["_", "__", *letter_list, digit])
    space = ast.Clazz("Space", ["space", "nbspace"])
    leading_symbol_liga = ast.Clazz("LeadingSymbolLiga", ["++", "--", "__"])
    symbol_before_greater = ast.Clazz(
        "SymbolBeforeGreater", ["|", "!", "~", "~", "#", "%"]
    )
    number = ast.Clazz("Number", ["+", "-", digit])
    eh = ast.Clazz("EH", ["=", "-"])

    surround = [
        [var, [space, ast.SPC, leading_symbol_liga]],
        [var, [ast.SPC, leading_symbol_liga]],
        [var, ast.clazz([var, number])],
        [ast.clazz([space, eh, symbol_before_greater]), None],
        [None, [space, number]],
        [None, ast.clazz(["/", number, eh])],
        ["`", "`"],
    ]

    return [
        ast.subst_liga(
            "<<",
            banner=[
                ast.ignore("<", "<", "<"),
                ast.ignore(None, "<", ["<", ast.clazz(["<", "~"])]),
            ],
        ),
        ast.subst_liga(
            "<<<",
            banner=[
                ast.ignore("<", "<", ["<", "<"]),
                ast.ignore(None, "<", ["<", "<", "<"]),
            ],
        ),
        ast.clazz_states(
            [
                var,
                space,
                leading_symbol_liga,
                symbol_before_greater,
                number,
                eh,
            ]
        ),
        ast.subst_liga(
            ">>",
            banner=[
                ast.ignore(ast.clazz(["<", "/", ">"]), ">", [">"]),
                ast.ignore(None, ">", [">", ">"]),
            ],
            surround=surround,
        ),
        ast.subst_liga(
            ">>>",
            banner=[
                ast.ignore(">", ">", [">", ">"]),
            ],
            surround=surround,
        ),
    ]
