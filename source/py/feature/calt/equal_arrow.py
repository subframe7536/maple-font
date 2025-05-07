from source.py.feature import ast
from source.py.feature.base.clazz import cls_normal_separator, cls_question


def get_lookup(cls_var: ast.Clazz):
    return [
        ast.subst_liga(
            "<=>",
            ign_prefix="<",
            ign_suffix=">",
            extra_rules=[
                ast.ignore(["(", cls_question], "<", ["=", ">"]),
            ],
        ),
        ast.subst_liga(
            "<==>",
            ign_prefix="<",
            ign_suffix=">",
            extra_rules=[
                ast.ignore(["(", cls_question], "<", ["=", "=", ">"]),
            ],
        ),
        ast.subst_liga(
            ">=",
            ign_prefix=ast.cls(">", "="),
            ign_suffix=ast.cls("<", ">", "=", cls_normal_separator),
        ),
        ast.subst_liga(
            "<=",
            ign_prefix=ast.cls("<", "="),
            ign_suffix=ast.cls("<", ">", "=", cls_normal_separator),
            extra_rules=[
                ast.ignore(["(", cls_question], "<", "="),
            ],
        ),
        ast.subst_liga(
            "<==",
            ign_prefix="<",
            ign_suffix=ast.cls("=", ">"),
            extra_rules=[
                ast.ignore(["(", cls_question], "<", ["=", "="]),
            ],
        ),
        ast.subst_liga(
            "==>",
            ign_prefix=ast.cls("[", "="),
            ign_suffix=">",
            extra_rules=[
                ast.ignore(["(", cls_question, "<"], "=", ["=", ">"]),
                ast.ignore(["(", cls_question], "=", ["=", ">"]),
            ],
        ),
        ast.subst_liga(
            "=>",
            ign_prefix=ast.cls("[", "=", ">", "|"),
            ign_suffix=ast.cls("=", ">"),
            extra_rules=[
                ast.ignore(["(", cls_question, "<"], "=", ">"),
                ast.ignore(["(", cls_question], "=", ">"),
            ],
        ),
        ast.subst_liga(
            "<=<",
            ign_prefix=ast.cls("<", "="),
            # `cls_var` is used to prevent confliction in Swift operator overload
            #
            # ```swift
            # public func <=<V: Value>(lhs: Expression<V>, rhs: Expression<V>) -> Expression<Bool> where V.Datatype: Comparable
            # ```
            ign_suffix=ast.cls("<", "=", cls_var),
            extra_rules=[
                ast.ignore(["(", cls_question], "<", ["=", "<"]),
            ],
        ),
        ast.subst_liga(
            ">=>",
            ign_prefix=ast.cls(">", "="),
            ign_suffix=ast.cls(">", "="),
        ),
        ast.subst_liga(
            "<=|",
            ign_prefix="<",
            ign_suffix=ast.cls("<", ">", "=", cls_normal_separator),
            extra_rules=[
                ast.ignore(["(", cls_question], "<", ["=", "|"]),
            ],
        ),
        ast.subst_liga(
            "|=>",
            ign_prefix=ast.cls("<", ">", "=", cls_normal_separator),
            ign_suffix=">",
        ),
    ]
