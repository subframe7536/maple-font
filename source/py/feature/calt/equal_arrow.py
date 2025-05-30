from source.py.feature import ast
from source.py.feature.base.clazz import cls_normal_separator, cls_question
from source.py.feature.calt._infinite_utils import (
    use_infinite,
    ignore_when_using_infinite,
    infinite_rules,
)


# Inspired by Fira Code, source:
# https://github.com/tonsky/FiraCode/blob/master/features/calt/equal_arrows.fea
def infinite_equals():
    eq_start = ast.gly_seq("=", "sta")
    eq_middle = ast.gly_seq("=", "mid")
    eq_end = ast.gly_seq("=", "end")
    cls_start = ast.Clazz("EqualStart", [eq_start, eq_middle])

    return ast.Lookup(
        "infinite_equal",
        " ".join(
            [
                "<=>",
                "<==>",
                "<==",
                "==>",
                "=>",
                "<=|",
                "|=>",
                "=<=",
                "=>=",
                "=======",
                ">=<",
            ]
        ),
        [
            cls_start.state(),
            ast.ign(None, "!", ["=", "="]),
            ast.ign("|", "|", "="),
            ast.ign("=", "|", "|"),
            ast.ign(["(", cls_question], "<", "="),
            ast.ign(["(", cls_question, "<"], "=", ast.cls("<", ">", "|", "=")),
            ast.ign(["(", cls_question, "<"], "=", ["=", ast.cls("<", ">", "|")]),
            # Disable >=</
            ast.ign(None, ">", ["=", ast.cls(ast.SPC, ">")]),
            # Disable >==</
            ast.ign(None, ">", ["=", "=", ast.SPC]),
            # Disable >===</
            ast.ign(None, ">", ["=", "=", "=", ast.SPC]),
            *infinite_rules(
                g="=",
                cls_start=cls_start,
                symbols=["<", ">", "|"],
                extra_rules=[
                    ast.subst(eq_end, ":", "=", ast.gly(":", ".case", True)),
                    # Disable >=<
                    ast.subst(
                        ">", "=", ["<", ast.cls("=", "<")], ast.gly_seq(">=", "sta")
                    ),
                    # Disable =<
                    ast.subst(None, "=", ["<", ast.cls("=", "<")], eq_start),
                ],
            ),
        ],
    )


def get_lookup(cls_var: ast.Clazz):
    return [
        ignore_when_using_infinite(
            ast.subst_liga(
                "<=>",
                ign_prefix=ast.cls("<", "="),
                ign_suffix=ast.cls(">", "="),
                extra_rules=[
                    ast.ign(["(", cls_question], "<", ["=", ">"]),
                ],
            ),
            ast.subst_liga(
                "<==>",
                ign_prefix=ast.cls("<", "="),
                ign_suffix=ast.cls(">", "="),
                extra_rules=[
                    ast.ign(["(", cls_question], "<", ["=", "=", ">"]),
                ],
            ),
        ),
        ast.subst_liga(
            ">=",
            ign_prefix=ast.cls(">", "="),
            ign_suffix=ast.cls("<", ">", "=", "!", ast.SPC, cls_normal_separator),
        ),
        ast.subst_liga(
            "<=",
            ign_prefix=ast.cls("<", "="),
            ign_suffix=ast.cls("<", ">", "=", "!", ast.SPC, cls_normal_separator),
            extra_rules=[
                ast.ign(["(", cls_question], "<", "="),
            ],
        ),
        ignore_when_using_infinite(
            ast.subst_liga(
                "<==",
                ign_prefix=ast.cls("<", "="),
                ign_suffix=ast.cls("=", ">", "<"),
                extra_rules=[
                    ast.ign(["(", cls_question], "<", ["=", "="]),
                ],
            ),
            ast.subst_liga(
                "==>",
                ign_prefix=ast.cls("[", "=", ">", "<"),
                ign_suffix=ast.cls(">", "="),
                extra_rules=[
                    ast.ign(["(", cls_question, "<"], "=", ["=", ">"]),
                    ast.ign(["(", cls_question], "=", ["=", ">"]),
                ],
            ),
            ast.subst_liga(
                "=>",
                ign_prefix=ast.cls("[", "=", ">", "|"),
                ign_suffix=ast.cls("=", ">"),
                extra_rules=[
                    ast.ign(["(", cls_question, "<"], "=", ">"),
                    ast.ign(["(", cls_question], "=", ">"),
                ],
            ),
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
                ast.ign(["(", cls_question], "<", ["=", "<"]),
            ],
        ),
        ast.subst_liga(
            ">=>",
            ign_prefix=ast.cls(">", "="),
            ign_suffix=ast.cls(">", "="),
        ),
        ignore_when_using_infinite(
            ast.subst_liga(
                "<=|",
                ign_prefix="<",
                ign_suffix=ast.cls("<", ">", "=", cls_normal_separator),
                extra_rules=[
                    ast.ign(["(", cls_question], "<", ["=", "|"]),
                ],
            ),
            ast.subst_liga(
                "|=>",
                ign_prefix=ast.cls("<", ">", "=", cls_normal_separator),
                ign_suffix=">",
            ),
        ),
        ast.subst_liga(
            "==",
            ign_prefix=ast.cls(":", "=", "!", "<", ">", "|"),
            ign_suffix=ast.cls(":", "=", "<", ">", "|"),
            extra_rules=[
                ast.ign(["(", cls_question], "=", "="),
                ast.ign(["(", cls_question, "<"], "=", "="),
            ],
        ),
        ast.subst_liga(
            "===",
            ign_prefix=ast.cls("=", "<", ">", "|", ":", ast.SPC),
            ign_suffix=ast.cls("=", "<", ">", "|", ":", ast.SPC),
            extra_rules=[
                ast.ign(["(", cls_question], "=", ["=", "="]),
                ast.ign(["(", cls_question, "<"], "=", ["=", "="]),
            ],
        ),
        ast.subst_liga(
            "!=",
            ign_prefix=ast.cls("!", "="),
            ign_suffix="=",
            extra_rules=[
                ast.ign(["(", cls_question], "!", "="),
                ast.ign(["(", cls_question, "<"], "!", "="),
            ],
        ),
        ast.subst_liga(
            "!==",
            ign_prefix=ast.cls("!", "="),
            ign_suffix=ast.cls("!", "="),
            extra_rules=[
                ast.ign(["(", cls_question], "!", ["=", "="]),
                ast.ign(["(", cls_question, "<"], "!", ["=", "="]),
            ],
        ),
        ast.subst_liga(
            "=/=",
            ign_prefix="=",
            ign_suffix="=",
            extra_rules=[
                ast.ign(["(", cls_question], "=", ["/", "="]),
                ast.ign(["(", cls_question, "<"], "=", ["/", "="]),
            ],
        ),
        ast.subst_liga(
            "=!=",
            ign_prefix="=",
            ign_suffix="=",
            extra_rules=[
                ast.ign(["(", cls_question], "=", ["!", "="]),
                ast.ign(["(", cls_question, "<"], "=", ["!", "="]),
            ],
        ),
        ignore_when_using_infinite(
            ast.subst_liga(
                "=<=",
                ign_prefix=ast.cls("=", ">", "<", "|"),
                ign_suffix=ast.cls("=", "<", ">"),
                extra_rules=[
                    ast.ign(["(", cls_question], "=", [">", "="]),
                ],
            ),
            ast.subst_liga(
                "=>=",
                ign_prefix=ast.cls("=", ">", "<", "|"),
                ign_suffix=ast.cls("=", "<", ">", "|"),
                extra_rules=[
                    ast.ign(["(", cls_question], "=", [">", "="]),
                ],
            ),
        ),
        ast.subst_liga(
            "|=",
            ign_prefix=ast.cls("|", "="),
            ign_suffix=ast.cls(">", "|", "="),
        ),
        infinite_equals() if use_infinite() else None,
    ]
