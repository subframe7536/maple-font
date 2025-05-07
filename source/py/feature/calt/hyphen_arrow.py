from source.py.feature import ast
from source.py.feature.base.clazz import cls_digit, cls_question


def get_lookup():
    return [
        ast.subst_liga(
            "<!--",
            ign_prefix="<",
            ign_suffix="-",
            extra_rules=[
                ast.ignore(["(", cls_question], "<", ["!", "-", "-"]),
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
    ]
