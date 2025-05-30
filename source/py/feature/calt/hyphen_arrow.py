from source.py.feature import ast
from source.py.feature.base.clazz import cls_digit, cls_question
from source.py.feature.calt._infinite_utils import (
    use_infinite,
    ignore_when_using_infinite,
    infinite_rules,
)


# Inspirde by Fira Code, source:
# https://github.com/tonsky/FiraCode/blob/master/features/calt/hyphen_arrows.fea
def infinite_hyphens():
    hy_start = ast.gly_seq("-", "sta")
    hy_middle = ast.gly_seq("-", "mid")
    cls_start = ast.Clazz("HyphenStart", [hy_start, hy_middle])

    return ast.Lookup(
        "infinite_hyphen",
        " ".join(
            [
                "<->",
                "<-->",
                "->",
                "<-",
                "-->",
                "<--",
                ">->",
                "<-<",
                "|->",
                "<-|",
                "-------",
                ">-",
                "-<",
                ">-<",
            ]
        ),
        [
            cls_start.state(),
            ast.ign(None, "<", [ast.cls("!", "#"), "-", "-"]),
            ast.ign("|", "|", "-"),
            ast.ign("-", "|", "|"),
            ast.ign("-", "-", "|"),
            ast.ign(["(", cls_question, "<", "!"], "-", "-"),
            ast.ign(">", "-", "<"),
            ast.ign(None, "<", ["-", ast.cls("+", "/", cls_digit)]),
            ast.ign(None, ">", ["-", ast.SPC]),
            ast.ign(None, "-", ["<", "/"]),
            *infinite_rules("-", cls_start, ["<", ">", "|"]),
        ],
    )


def get_lookup():
    return [
        ast.subst_liga(
            "--",
            ign_prefix=ast.cls("<", ">", "-", "|"),
            ign_suffix=ast.cls("<", ">", "-", "|"),
            extra_rules=[
                ast.ign(["<", ast.cls("#", "!")], "-", "-"),
                ast.ign(
                    ["(", cls_question, "<", "!"],
                    "-",
                    "-",
                ),
            ],
        ),
        ast.subst_liga(
            "---",
            ign_prefix=ast.cls("<", ">", "-", "|", ast.SPC),
            ign_suffix=ast.cls("<", ">", "-", "|", ast.SPC),
            extra_rules=[
                ast.ign("<", "-", ["-", "-", ">"]),
            ],
        ),
        ast.subst_liga(
            "<!--",
            ign_prefix="<",
            ign_suffix="-",
            extra_rules=[
                ast.ign(["(", cls_question], "<", ["!", "-", "-"]),
            ],
        ),
        ast.subst_liga(
            "<#--",
            ign_prefix="<",
            ign_suffix="-",
        ),
        ast.subst_liga("<!---->", target="xml_empty_comment.liga"),
        ignore_when_using_infinite(
            ast.subst_liga(
                "<->",
                ign_prefix=ast.cls("<", "-"),
                ign_suffix=ast.cls(">", "-"),
            ),
            ast.subst_liga(
                "->",
                ign_prefix=ast.cls("-", "<", ">", "|", "+"),
                ign_suffix=ast.cls(">", "-"),
            ),
            ast.subst_liga(
                "<-",
                ign_prefix=ast.cls("<", "-"),
                ign_suffix=ast.cls("-", "<", ">", "|", "+", "/", cls_digit),
            ),
            ast.subst_liga(
                "-->",
                ign_prefix=ast.cls("-", "<", ">", "|"),
                ign_suffix=ast.cls(">", "-"),
            ),
            ast.subst_liga(
                "<--",
                ign_prefix=ast.cls("<", "|"),
                ign_suffix=ast.cls("-", "<", ">", "|"),
            ),
            ast.subst_liga(
                "<-<",
                ign_prefix=ast.cls("<", "|", "-"),
                ign_suffix=ast.cls("<", "|", "-"),
            ),
            ast.subst_liga(
                ">->",
                ign_prefix=ast.cls(">", "|", "-"),
                ign_suffix=ast.cls(">", "|", "-"),
            ),
            ast.subst_liga(
                "<-|",
                ign_prefix=ast.cls("<", "-"),
                ign_suffix=ast.cls("|", "-"),
            ),
            ast.subst_liga(
                "|->",
                ign_prefix=ast.cls("|", "-"),
                ign_suffix=ast.cls(">", "-"),
            ),
        ),
        infinite_hyphens() if use_infinite() else None,
    ]
