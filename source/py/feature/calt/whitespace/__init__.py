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
            banner=[
                ast.ignore("[", "[", "|"),
                ast.ignore(None, "[", ["|", ast.cls("]", "|")]),
            ],
        ),
        ast.subst_liga(
            "|]",
            banner=[
                ast.ignore(ast.cls("[", "|"), "|", "]"),
                ast.ignore(None, "|", ["]", "]"]),
            ],
        ),
        ast.subst_liga(
            "!!",
            banner=[
                ast.ignore("!", "!", "!"),
                ast.ignore(None, "!", ["!", "!"]),
                ast.ignore(["(", cls_question], "!", "!"),
                ast.ignore(["(", cls_question, "<"], "!", "!"),
            ],
        ),
        ast.subst_liga(
            "||",
            banner=[
                ast.ignore(ast.cls("-", "|", "[", "<"), "|", "|"),
                ast.ignore(None, "|", ["|", ast.cls("|", "]", ">", "-", "=")]),
            ],
        ),
        ast.subst_liga(
            2 * [cls_question.use()],
            target=ast.gly("??"),
            desc="??",
            banner=[
                ast.ignore(cls_question, cls_question, cls_question),
                ast.ignore(None, cls_question, [cls_question, ast.cls(cls_question, "=")]),
            ],
        ),
        ast.subst_liga(
            3 * [cls_question.use()],
            target=ast.gly("???"),
            desc="???",
            banner=[
                ast.ignore(cls_question, cls_question, [cls_question, cls_question]),
                ast.ignore(
                    None, cls_question, [cls_question, cls_question, cls_question]
                ),
            ],
        ),
        ast.subst_liga(
            "&&",
            banner=[
                ast.ignore("&", "&", "&"),
                ast.ignore(None, "&", ["&", ast.cls("&", "=")]),
            ],
        ),
        ast.subst_liga(
            "&&&",
            banner=[
                ast.ignore("&", "&", ["&", "&"]),
                ast.ignore(None, "&", ["&", "&", "&"]),
            ],
        ),
        ast.subst_liga(
            "//",
            banner=[
                ast.ignore("/", "/", "/"),
                ast.ignore(None, "/", ["/", ast.cls("/", "=")]),
            ],
        ),
        ast.subst_liga(
            "///",
            banner=[
                ast.ignore("/", "/", ["/", "/"]),
                ast.ignore(None, "/", ["/", "/", "/"]),
            ],
        ),
        ast.subst_liga(
            "/*",
            banner=[
                ast.ignore(ast.cls("/", "*"), "/", "*"),
                ast.ignore(None, "/", ["*", ast.cls("/", "*", ".")]),
            ],
        ),
        ast.subst_liga(
            "/**",
            banner=[
                ast.ignore(ast.cls("/", "*"), "/", ["*", "*"]),
                ast.ignore(None, "/", ["*", "*", ast.cls("/", "*", ".")]),
            ],
        ),
        ast.subst_liga(
            "*/",
            banner=[
                ast.ignore(ast.cls("/", "*", "."), "*", "/"),
                ast.ignore(None, "*", ["/", ast.cls("/", "*")]),
            ],
        ),
        ast.subst_liga(
            "++",
            banner=[
                ast.ignore(ast.cls("+", ":"), "+", "+"),
                ast.ignore(None, "+", ["+", ast.cls("+", ":")]),
            ],
        ),
        ast.subst_liga(
            "+++",
            banner=[
                ast.ignore("+", "+", ["+", "+"]),
                ast.ignore(None, "+", ["+", "+", "+"]),
            ],
        ),
        ast.subst_liga(
            "--",
            banner=[
                ast.ignore(ast.cls("<", "-"), "-", "-"),
                ast.ignore(["<", ast.cls("#", "!")], "-", "-"),
                ast.ignore(None, "-", ["-", ast.cls("-", ">")]),
                ast.ignore(
                    ["(", cls_question, "<", "!"],
                    "-",
                    "-",
                ),
                ast.ignore(
                    ast.cls("<", "-"),
                    "-",
                    "-",
                ),
            ],
        ),
        ast.subst_liga(
            "---",
            banner=[
                ast.ignore("<", "-", ["-", "-", ">"]),
                ast.ignore("-", "-", ["-", "-"]),
                ast.ignore(None, "-", ["-", "-", "-"]),
            ],
        ),
        ast.subst_liga(
            ";;",
            banner=[
                ast.ignore(";", ";", ";"),
                ast.ignore(None, ";", [";", ";"]),
            ],
        ),
        ast.subst_liga(
            ";;;",
            banner=[
                ast.ignore(";", ";", [";", ";"]),
                ast.ignore(None, ";", [";", ";", ";"]),
            ],
        ),
        ast.subst_liga(
            "..",
            banner=[
                ast.ignore(".", ".", "."),
                ast.ignore(None, ".", [".", ast.cls(".", "<", cls_question)]),
            ],
        ),
        ast.subst_liga(
            "...",
            banner=[
                ast.ignore(".", ".", [".", "."]),
                ast.ignore(None, ".", [".", ".", ast.cls(".", "<", cls_question)]),
            ],
        ),
        ast.subst_liga(
            [ast.gly("."), cls_question.use()],  # Zig
            target=ast.gly(".?"),
            desc=".?",
            banner=[
                ast.ignore(".", ".", cls_question),
                ast.ignore(None, ".", [cls_question, cls_question]),
            ],
        ),
        ast.subst_liga(
            [cls_question.use(), ast.gly(".")],  # TypeScript / Rust
            target=ast.gly("?."),
            desc="?.",
            banner=[
                ast.ignore(cls_question, cls_question, "."),
                ast.ignore(None, cls_question, [".", ast.cls(".", "=", cls_question)]),
            ],
        ),
        ast.subst_liga(
            "..<",  # Swift / Kotlin
            banner=[
                ast.ignore(".", ".", [".", "<"]),
                ast.ignore(None, ".", [".", "<", ast.cls("<", "/", ">")]),
            ],
        ),
        ast.subst_liga(
            ".=",  # Swift
            banner=[
                ast.ignore(".", ".", "="),
                ast.ignore(None, ".", ["=", ast.cls("=", ">")]),
            ],
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
