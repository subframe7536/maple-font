from source.py.feature import ast
from source.py.feature.base.clazz import cls_question
from source.py.feature.calt._infinite_utils import infinite_helper, infinite_rules


# Inspired by Fira Code, source:
# https://github.com/tonsky/FiraCode/blob/master/features/calt/equal_arrows.fea
def infinite_equals():
    if not infinite_helper.get():
        return None

    eq_start = ast.gly_seq("=", "sta")
    eq_middle = ast.gly_seq("=", "mid")
    eq_end = ast.gly_seq("=", "end")
    cls_start = ast.Clazz("EqualStart", [eq_start, eq_middle])
    colon_case = ast.gly(":", ".case", True)

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
                ":=",
                "=:",
                ":=:",
                "=:=",
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
            ast.ign(None, ">", ["=", ast.SPC, ast.gly("</")]),
            ast.ign(None, ">", ["=", "<", "/"]),
            # Disable >==</
            ast.ign(None, ">", ["=", "=", ast.SPC, ast.gly("</")]),
            ast.ign(None, ">", ["=", "=", "<", "/"]),
            # Disable >===</
            ast.ign(None, ">", ["=", "=", "=", ast.SPC, ast.gly("</")]),
            ast.ign(None, ">", ["=", "=", "=", "<", "/"]),
            ast.ign(">", "=", ["=", "=", ast.SPC, ast.gly("</")]),
            ast.ign(">", "=", ["=", "=", "<", "/"]),
            ast.ign([">", "="], "=", ["=", ast.SPC, ast.gly("</")]),
            ast.ign([">", "="], "=", ["=", "<", "/"]),
            *infinite_rules(
                glyph="=",
                cls_start=cls_start,
                symbols=["<", ">", "|"],
                extra_rules=[
                    # Colon support
                    ast.ign(":", ":", "="),
                    ast.ign(eq_end, ":", ":"),
                    ast.subst(None, ":", "=", colon_case),
                    ast.subst(ast.cls(["=", eq_end]), ":", None, colon_case),
                    # Disable =<
                    ast.subst(None, "=", ["<", "="], eq_start),
                    ast.ign(None, "=", "<"),
                ],
            ),
        ],
    )


def get_lookup(cls_var: ast.Clazz):
    return [
        infinite_helper.ignore_when_enabled(
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
            ign_prefix=ast.cls(">", "=", "|"),
            ign_suffix=ast.cls("<", ">", "=", "!", ast.SPC),
        ),
        ast.subst_liga(
            "<=",
            ign_prefix=ast.cls("<", "="),
            ign_suffix=ast.cls("<", ">", "=", "!", "|", ast.SPC),
            extra_rules=[
                ast.ign(["(", cls_question], "<", "="),
            ],
        ),
        infinite_helper.ignore_when_enabled(
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
        infinite_helper.ignore_when_enabled(
            ast.subst_liga(
                "<=|",
                ign_prefix="<",
                ign_suffix=ast.cls("<", ">", "=", "|"),
                extra_rules=[
                    ast.ign(["(", cls_question], "<", ["=", "|"]),
                ],
            ),
            ast.subst_liga(
                "|=>",
                ign_prefix=ast.cls("<", ">", "=", "|"),
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
        infinite_helper.ignore_when_disabled(
            ast.subst_liga(
                "===",
                lookup_name=ast.gly("===", "__ALT__"),
                desc=">===</",
                surround=[
                    (">", [ast.SPC, ast.gly("</")]),
                    (">", ["<", "/"]),
                ],
            )
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
        infinite_helper.ignore_when_enabled(
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
        infinite_equals(),
    ]
