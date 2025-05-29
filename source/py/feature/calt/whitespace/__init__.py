from source.py.feature import ast
from source.py.feature.base.clazz import cls_question
from source.py.feature.calt.whitespace import (
    brace,
    colon,
    multiple_compare,
    numbersign_underscore,
    upper,
)


def get_base_lookup():
    return [
        ast.subst_liga(
            "[|",
            ign_prefix="[",
            ign_suffix=ast.cls("]", "|"),
        ),
        ast.subst_liga(
            "|]",
            ign_prefix=ast.cls("[", "|"),
            ign_suffix="]",
        ),
        ast.subst_liga(
            "!!",
            ign_prefix="!",
            ign_suffix="!",
            extra_rules=[
                ast.ign(["(", cls_question], "!", "!"),
                ast.ign(["(", cls_question, "<"], "!", "!"),
            ],
        ),
        ast.subst_liga(
            "||",
            ign_prefix=ast.cls("|", "[", "<"),
            ign_suffix=ast.cls("|", "]", ">"),
        ),
        ast.subst_liga(
            2 * [cls_question.use()],
            target=ast.gly("??"),
            desc="??",
            ign_prefix=cls_question,
            ign_suffix=cls_question,
        ),
        ast.subst_liga(
            3 * [cls_question.use()],
            target=ast.gly("???"),
            desc="???",
            ign_prefix=cls_question,
            ign_suffix=cls_question,
        ),
        ast.subst_liga(
            "&&",
            ign_prefix="&",
            ign_suffix="&",
        ),
        ast.subst_liga(
            "&&&",
            ign_prefix="&",
            ign_suffix="&",
        ),
        ast.subst_liga(
            "//",
            ign_prefix="/",
            ign_suffix="/",
        ),
        ast.subst_liga(
            "///",
            ign_prefix="/",
            ign_suffix="/",
        ),
        ast.subst_liga(
            "/*",
            ign_prefix=ast.cls("/", "*"),
            ign_suffix=ast.cls("/", "*", "."),
        ),
        ast.subst_liga(
            "/**",
            ign_prefix=ast.cls("/", "*"),
            ign_suffix=ast.cls("/", "*", "."),
        ),
        ast.subst_liga(
            "*/",
            ign_prefix=ast.cls("/", "*", "."),
            ign_suffix=ast.cls("/", "*"),
        ),
        ast.subst_liga(
            "++",
            ign_prefix=ast.cls("+", ":"),
            ign_suffix=ast.cls("+", ":"),
        ),
        ast.subst_liga(
            "+++",
            ign_prefix="+",
            ign_suffix="+",
        ),
        ast.subst_liga(
            ";;",
            ign_prefix=";",
            ign_suffix=";",
        ),
        ast.subst_liga(
            ";;;",
            ign_prefix=";",
            ign_suffix=";",
        ),
        ast.subst_liga(
            "..",
            ign_prefix=".",
            ign_suffix=ast.cls(".", "<", cls_question),
        ),
        ast.subst_liga(
            "...",
            ign_prefix=".",
            ign_suffix=ast.cls(".", "<", cls_question),
        ),
        ast.subst_liga(
            [ast.gly("."), cls_question.use()],  # Zig
            target=ast.gly(".?"),
            desc=".?",
            ign_prefix=".",
            ign_suffix=cls_question,
        ),
        ast.subst_liga(
            [cls_question.use(), ast.gly(".")],  # TypeScript / Rust
            target=ast.gly("?."),
            desc="?.",
            ign_prefix=cls_question,
            ign_suffix=ast.cls(".", "=", cls_question),
        ),
        ast.subst_liga(
            "..<",  # Swift / Kotlin
            ign_prefix=".",
            ign_suffix=ast.cls("<", "/", ">"),
        ),
        ast.subst_liga(
            ".=",  # Swift
            ign_prefix=".",
            ign_suffix=ast.cls("=", ">"),
        ),
    ]


def get_lookup(cls_var: ast.Clazz):
    return (
        upper.get_lookup()
        + colon.get_lookup()
        + numbersign_underscore.get_lookup()
        + multiple_compare.get_lookup(cls_var)
        + brace.get_lookup()
        + get_base_lookup()
    )
