from source.py.feature import ast
from source.py.feature.base.clazz import cls_digit, cls_question
from source.py.feature.calt._common import infinite_rules

# Inspirde by Fira Code, source:
# https://github.com/tonsky/FiraCode/blob/master/features/calt/hyphen_arrows.fea
def infinite_hyphens(cls_var: ast.Clazz):
    hy_start = ast.gly_seq("-", "sta")
    hy_middle = ast.gly_seq("-", "mid")
    cls_start = ast.Clazz("HyphenStart", [hy_start, hy_middle])

    return ast.Lookup(
        "infinity_hyphen",
        "-------",
        [
            cls_start.state(),
            ast.ign(None, "<", [ast.cls("!", "#"), "-", "-"]),
            ast.ign("|", "|", "-"),
            ast.ign("-", "|", "|"),
            ast.ign(">", "-", "<"),
            ast.ign(cls_var, ">", "-"),
            # Main rules
            *infinite_rules("-", cls_start, ["<", ">", "|"]),
            # Disable >-<
            ast.subst(">", "-", ["<", ast.cls("-", "<")], ast.gly_seq(">-", "sta")),
            # Disable -<
            ast.subst(None, "-", ["<", ast.cls("-", "<")], hy_start),
        ],
    )


def get_lookup(cls_var: ast.Clazz):
    return [
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
        ast.subst_liga(
            "<->",
            ign_prefix="<",
            ign_suffix=">",
        ),
        ast.subst_liga(
            "->",
            ign_prefix=ast.cls("-", "<", ">", "|", "+"),
            ign_suffix=">",
        ),
        ast.subst_liga(
            "<-",
            ign_prefix="<",
            ign_suffix=ast.cls("-", "<", ">", "|", "+", "/", cls_digit),
        ),
        ast.subst_liga(
            "-->",
            ign_prefix="-",
            ign_suffix=">",
        ),
        ast.subst_liga(
            "<--",
            ign_prefix="<",
            ign_suffix="-",
        ),
        ast.subst_liga(
            "<-<",
            ign_prefix="<",
            ign_suffix="<",
        ),
        ast.subst_liga(
            ">->",
            ign_prefix=">",
            ign_suffix=">",
        ),
        ast.subst_liga(
            "<-|",
            ign_prefix="<",
            ign_suffix="|",
        ),
        ast.subst_liga(
            "|->",
            ign_prefix="|",
            ign_suffix=">",
        ),
        infinite_hyphens(cls_var)
    ]
