from source.py.feature import ast
from source.py.feature.base.clazz import digit


def get_lookup(cls_var: ast.Clazz):
    cls_space = ast.Clazz("Space", ["space", "nbspace"])
    cls_leading_symbol_liga = ast.Clazz("LeadingSymbolLiga", ["++", "--", "__"])
    cls_symbol_before_greater = ast.Clazz(
        "SymbolBeforeGreater", ["|", "!", "~", "~", "#", "%"]
    )
    cls_number = ast.Clazz("Number", ["+", "-", digit])
    cls_equal_hyphen = ast.Clazz("EqualHyphen", ["=", "-"])

    surround = [
        [cls_var, [cls_space, ast.SPC, cls_leading_symbol_liga]],
        [cls_var, [ast.SPC, cls_leading_symbol_liga]],
        [cls_var, ast.clazz([cls_var, cls_number])],
        [ast.clazz([cls_space, cls_equal_hyphen, cls_symbol_before_greater]), None],
        [None, [cls_space, cls_number]],
        [None, ast.clazz(["/", cls_number, cls_equal_hyphen])],
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
                cls_space,
                cls_leading_symbol_liga,
                cls_symbol_before_greater,
                cls_number,
                cls_equal_hyphen,
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
