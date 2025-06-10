from source.py.feature import ast
from source.py.feature.base.clazz import cls_question
from source.py.feature.calt._infinite_utils import infinite_helper


def get_lookup():
    cls_ign_colon = ast.Clazz("IgnoreColon", ["<", ":", ">", "="])
    cls_ign_markup = ast.Clazz("IgnoreMarkup", ["<", "/", ">"])

    return [
        ast.subst_liga(
            "::",
            ign_prefix=":",
            ign_suffix=":",
        ),
        ast.subst_liga(
            ":::",
            ign_prefix=":",
            ign_suffix=":",
        ),
        ast.subst_liga(
            [cls_question.use(), ast.gly(":")],
            target=ast.gly("?:"),
            desc="?:",
            ign_prefix=cls_question,
            ign_suffix=ast.cls(":", "="),
        ),
        ast.subst_liga(
            [ast.gly(":"), cls_question.use()],
            target=ast.gly(":?"),
            desc=":?",
            ign_prefix=":",
            ign_suffix=ast.cls(cls_question, ">"),
        ),
        ast.subst_liga(
            [ast.gly(":"), cls_question.use(), ast.gly(">")],
            target=ast.gly(":?>"),
            desc=":?>",
            ign_prefix=":",
            ign_suffix=">",
        ),
        ast.cls_states(
            cls_ign_colon,
            cls_ign_markup,
        ),
        infinite_helper.ignore_when_using(
            ast.subst_liga(
                ":=",
                ign_prefix=ast.cls(cls_ign_colon, cls_question),
                ign_suffix=ast.cls("=", ":"),
            ),
            ast.subst_liga(
                "=:",
                ign_prefix=cls_ign_colon,
                ign_suffix=ast.cls("=", ":"),
                extra_rules=[
                    ast.ign(["(", cls_question], "=", ":"),
                ],
            ),
            ast.subst_liga(
                ":=:",
                ign_prefix=ast.cls(cls_ign_colon, cls_question),
                ign_suffix=ast.cls(cls_ign_colon, cls_question),
                extra_rules=[
                    ast.ign(["(", cls_question], ":", ["=", ":"]),
                ],
            ),
            ast.subst_liga(
                "=:=",
                ign_prefix="=",
                ign_suffix="=",
                extra_rules=[
                    ast.ign(["(", cls_question], "=", [":", "="]),
                ],
            ),
            ast.subst_liga(
                "::=",
                ign_prefix=":",
                ign_suffix="=",
            ),
        ),
        ast.subst_liga(
            "<:",
            ign_prefix="<",
            ign_suffix=cls_ign_colon,
        ),
        ast.subst_liga(
            ":>",
            ign_prefix=cls_ign_colon,
            ign_suffix=">",
        ),
        ast.subst_liga(
            ":<",
            ign_prefix=cls_ign_colon,
            ign_suffix=cls_ign_markup,
        ),
        ast.subst_liga(
            "<:<",  # scala / haskell
            ign_prefix="<",
            ign_suffix=cls_ign_markup,
        ),
        ast.subst_liga(
            ">:>",  # scala / haskell
            ign_prefix=cls_ign_markup,
            ign_suffix=">",
        ),
    ]
