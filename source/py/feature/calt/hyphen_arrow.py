from source.py.feature import ast
from source.py.feature.base.clazz import cls_digit, cls_question
from source.py.feature.calt._infinite_utils import infinite_helper, infinite_rules


# Inspirde by Fira Code, source:
# https://github.com/tonsky/FiraCode/blob/master/features/calt/hyphen_arrows.fea
def infinite_hyphens(cls_var: ast.Clazz):
    if not infinite_helper.get():
        return None

    hy_start = ast.gly_seq("-", "sta")
    hy_middle = ast.gly_seq("-", "mid")
    ghy_start = ast.gly_seq(">-", "sta")
    ghy_middle = ast.gly_seq(">-", "mid")
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
                ">--",
                "--<",
            ]
        ),
        [
            cls_start.state(),
            ast.ign(None, "<", [ast.cls("!", "#"), "-", "-"]),
            ast.ign(ast.cls("|", "+"), "|", "-"),
            ast.ign(None, "|", ["-", "-", cls_var]),
            ast.ign("|", "-", ["-", cls_var]),
            ast.ign(None, "|", ["-", "-", "<", cls_var]),
            ast.ign("|", "-", ["-", "<", cls_var]),
            ast.ign("-", "|", "|"),
            ast.ign("-", "-", "|"),
            ast.ign(["(", cls_question, "<", "!"], "-", "-"),
            ast.ign(None, "<", ["-", ast.cls("+", "/", cls_digit)]),
            ast.ign(None, "-", ["<", "/"]),
            # # Disable >-</
            # ast.ign(None, ">", ["-", ast.cls(ast.SPC, ">")]),
            # ast.ign(None, ">", ["-", "<", "/"]),
            # Disable >--</
            ast.ign(None, ">", ["-", "-", ast.SPC, ast.gly("</")]),
            ast.ign(None, ">", ["-", "-", "<", "/"]),
            ast.ign(">", "-", ["-", ast.SPC, ast.gly("</")]),
            ast.ign(">", "-", ["-", "<", "/"]),
            # Disable >---</
            ast.ign(None, ">", ["-", "-", "-", ast.SPC, ast.gly("</")]),
            ast.ign(None, ">", ["-", "-", "-", "<", "/"]),
            ast.ign(">", "-", ["-", "-", ast.SPC, ast.gly("</")]),
            ast.ign(">", "-", ["-", "-", "<", "/"]),
            ast.ign([">", "-"], "-", ["-", ast.SPC, ast.gly("</")]),
            ast.ign([">", "-"], "-", ["-", "<", "/"]),
            # Disable >-
            ast.subst(cls_start, ">", "-", ghy_middle),
            ast.subst(None, ">", ["-", ast.cls("-", "|", ">")], ghy_start),
            ast.subst(None, ">", ["-", "<", "-"], ghy_start),
            ast.ign(None, ">", "-"),
            # Disable -<
            ast.subst(
                ast.cls(
                    ghy_middle,
                    ast.gly_seq("<-", "sta"),
                    ast.gly_seq("<-", "mid"),
                    ast.gly_seq("|-", "sta"),
                    ast.gly_seq("|-", "mid"),
                    ghy_start,
                    cls_start,
                ),
                "-",
                "<",
                hy_middle,
            ),
            ast.subst(None, "-", ["<", "-"], hy_start),
            ast.ign(None, "-", "<"),
            # Disable >-<
            ast.subst(None, ">", ["-", "<", "-"], ghy_start),
            ast.subst("-", ">", ["-", "<"], ghy_middle),
            ast.ign(None, ">", ["-", "<"]),
            *infinite_rules(glyph="-", cls_start=cls_start, symbols=["<", ">", "|"]),
        ],
    )


def get_lookup(cls_var: ast.Clazz):
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
            surround=[
                (None, None),
                ("|", [cls_var]),
                ("|", ["<", cls_var]),
            ],
        ),
        ast.subst_liga(
            "--",
            lookup_name=ast.gly("--", "__REGEX__"),
            extra_rules=[ast.ign(ast.cls("<", ">", "-", "!"), "-", ["-", "<"])],
            surround=[
                ("|", [cls_var]),
                (None, ["<", cls_var]),
            ],
        ),
        infinite_helper.ignore_when_disabled(
            ast.subst_liga(
                "--",
                lookup_name=ast.gly("--", "__ALT__"),
                desc=">--</",
                surround=[
                    (">", [ast.SPC, ast.gly("</")]),
                    (">", ["<", "/"]),
                ],
            )
        ),
        ast.subst_liga(
            "---",
            ign_prefix=ast.cls("<", ">", "-", "|", ast.SPC),
            ign_suffix=ast.cls("<", ">", "-", "|", ast.SPC),
            extra_rules=[
                ast.ign("<", "-", ["-", "-", ">"]),
            ],
        ),
        infinite_helper.ignore_when_disabled(
            ast.subst_liga(
                "---",
                lookup_name=ast.gly("---", "__ALT__"),
                desc=">---</",
                surround=[
                    (">", [ast.SPC, ast.gly("</")]),
                    (">", ["<", "/"]),
                ],
            )
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
        infinite_helper.ignore_when_enabled(
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
        infinite_hyphens(cls_var),
    ]
