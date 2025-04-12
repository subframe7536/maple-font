from source.py.feature import ast
from source.py.feature.base.clazz import cls_normal_separator, cls_question


def get_lookup(cls_var: ast.Clazz):
    return [
        ast.subst_liga(
            "<=>",
            banner=[
                ast.ignore("<", "<", ["=", ">"]),
                ast.ignore(None, "<", ["=", ">", ">"]),
                ast.ignore(["(", cls_question], "<", ["=", ">"]),
            ],
        ),
        ast.subst_liga(
            "<==>",
            banner=[
                ast.ignore("<", "<", ["=", "=", ">"]),
                ast.ignore(None, "<", ["=", "=", ">", ">"]),
                ast.ignore(["(", cls_question], "<", ["=", "=", ">"]),
            ],
        ),
        ast.subst_liga(
            ">=",
            banner=[
                ast.ignore(ast.cls(">", "="), ">", "="),
                ast.ignore(
                    None,
                    ">",
                    ["=", ast.cls("<", ">", "=", cls_question, cls_normal_separator)],
                ),
            ],
        ),
        ast.subst_liga(
            "<=",
            banner=[
                ast.ignore(ast.cls("<", "="), "<", "="),
                ast.ignore(
                    None, "<", ["=", ast.cls("<", ">", "=", cls_normal_separator)]
                ),
                ast.ignore(["(", cls_question], "<", "="),
            ],
        ),
        ast.subst_liga(
            "<==",
            banner=[
                ast.ignore("<", "<", ["=", "="]),
                ast.ignore(None, "<", ["=", "=", ast.cls("=", ">")]),
                ast.ignore(["(", cls_question], "<", ["=", "="]),
            ],
        ),
        ast.subst_liga(
            "==>",
            banner=[
                ast.ignore(ast.cls("[", "="), "=", ["=", ">"]),
                ast.ignore(None, "=", ["=", ">", ">"]),
                ast.ignore(["(", cls_question, "<"], "=", ["=", ">"]),
                ast.ignore(["(", cls_question], "=", ["=", ">"]),
            ],
        ),
        ast.subst_liga(
            "=>",
            banner=[
                ast.ignore(ast.cls("[", "=", ">", "|"), "=", ">"),
                ast.ignore(None, "=", [">", ast.cls("=", ">")]),
                ast.ignore(["(", cls_question, "<"], "=", ">"),
                ast.ignore(["(", cls_question], "=", ">"),
            ],
        ),
        ast.subst_liga(
            "<=<",
            banner=[
                ast.ignore(ast.cls("<", "="), "<", ["=", "<"]),
                # `cls_var` is used to prevent confliction in Swift operator overload
                #
                # ```swift
                # public func <=<V: Value>(lhs: Expression<V>, rhs: Expression<V>) -> Expression<Bool> where V.Datatype: Comparable
                # ```
                ast.ignore(None, "<", ["=", "<", ast.cls("<", "=", cls_var)]),
                ast.ignore(["(", cls_question], "<", ["=", "<"]),
            ],
        ),
        ast.subst_liga(
            ">=>",
            banner=[
                ast.ignore(ast.cls(">", "="), ">", ["=", ">"]),
                ast.ignore(None, ">", ["=", ">", ast.cls(">", "=")]),
            ],
        ),
        ast.subst_liga(
            "<=|",
            banner=[
                ast.ignore("<", "<", ["=", "|"]),
                ast.ignore(
                    None,
                    "<",
                    ["=", "|", ast.cls("<", ">", "=", cls_normal_separator)],
                ),
                ast.ignore(["(", cls_question], "<", ["=", "|"]),
            ],
        ),
        ast.subst_liga(
            "|=>",
            banner=[
                ast.ignore(
                    ast.cls("<", ">", "=", cls_normal_separator), "|", ["=", ">"]
                ),
                ast.ignore(None, "|", ["=", ">", ">"]),
            ],
        ),
    ]
