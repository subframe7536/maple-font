from source.py.feature import ast
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
                ast.ignore(["(", "?"], "!", "!"),
                ast.ignore(["(", "?", "<"], "!", "!"),
            ],
        ),
        ast.subst_liga(
            "||",
            banner=[
                ast.ignore(ast.cls("-", "|", "[", "<"), "|", "|"),
                ast.ignore(None, "|", ["|", ast.cls("|", "]", ">", "-")]),
            ],
        ),
        ast.subst_liga(
            "??",
            banner=[
                ast.ignore("?", "?", "?"),
                ast.ignore(None, "?", ["?", "?"]),
            ],
        ),
        ast.subst_liga(
            "???",
            banner=[
                ast.ignore("?", "?", ["?", "?"]),
                ast.ignore(None, "?", ["?", "?", "?"]),
            ],
        ),
        ast.subst_liga(
            "&&",
            banner=[
                ast.ignore("&", "&", "&"),
                ast.ignore(None, "&", ["&", "&"]),
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
                    ["(", "?", "<", "!"],
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
                ast.ignore(None, ".", [".", ast.cls(".", "<", "?")]),
            ],
        ),
        ast.subst_liga(
            "...",
            banner=[
                ast.ignore(".", ".", [".", "."]),
                ast.ignore(None, ".", [".", ".", ast.cls(".", "<", "?")]),
            ],
        ),
        ast.subst_liga(
            ".?",  # Zig
            banner=[
                ast.ignore(".", ".", "?"),
                ast.ignore(None, ".", ["?", "?"]),
            ],
        ),
        ast.subst_liga(
            "?.",  # TypeScript / Rust
            banner=[
                ast.ignore("?", "?", "."),
                ast.ignore(None, "?", [".", ast.cls(".", "=", "?")]),
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
