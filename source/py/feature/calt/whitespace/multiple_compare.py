from source.py.feature import ast
from source.py.feature.base.clazz import cls_digit, cls_space


def get_lookup(cls_var: ast.Clazz):
    cls_leading_symbol_liga = ast.Clazz("LeadingSymbolLiga", ["++", "--", "__"])
    cls_equal_hyphen = ast.Clazz("EqualHyphen", ["=", "-"])
    cls_symbol_before_greater = ast.Clazz(
        "SymbolBeforeGreater",
        ["|", "!", "~", "~", "#", "%", cls_space, cls_equal_hyphen],
    )
    cls_number = ast.Clazz("Number", ["+", "-", cls_digit])
    cls_quote_like = ast.Clazz("QuoteLike", ["`", "'", '"'])

    surround = [
        (cls_var, [cls_space, ast.SPC, cls_leading_symbol_liga]),
        (cls_var, [ast.SPC, cls_leading_symbol_liga]),
        (cls_var, ast.cls(cls_var, cls_number)),
        (cls_symbol_before_greater, None),
        (None, [cls_space, cls_number]),
        (None, ast.cls("/", cls_number, cls_equal_hyphen)),
        (cls_quote_like, cls_quote_like),
    ]

    return [
        ast.subst_liga(
            "<<",
            banner=[
                ast.ignore("<", "<", "<"),
                ast.ignore(None, "<", ["<", ast.cls("<", "~")]),
            ],
        ),
        ast.subst_liga(
            "<<<",
            banner=[
                ast.ignore("<", "<", ["<", "<"]),
                ast.ignore(None, "<", ["<", "<", "<"]),
            ],
        ),
        ast.cls_states(
            cls_leading_symbol_liga,
            cls_equal_hyphen,
            cls_symbol_before_greater,
            cls_number,
            cls_quote_like,
        ),
        ast.subst_liga(
            ">>",
            banner=[
                ast.ignore(ast.cls("<", "/", ">"), ">", [">"]),
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
