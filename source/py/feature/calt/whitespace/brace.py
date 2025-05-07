from source.py.feature import ast


def get_lookup():
    return [
        ast.Lookup(
            ast.gly("{{"),
            "{{",
            [
                ast.ignore("{", "{", "{"),
                ast.ignore(None, "{", ["{", ast.cls("{", "!", "-")]),
                ast.subst(None, "{", "{", ast.gly_var("{", "start")),
                ast.subst(
                    ast.gly_var("{", "start"), "{", None, ast.gly_var("{", "end")
                ),
            ],
        ),
        ast.Lookup(
            ast.gly("}}"),
            "}}",
            [
                ast.ignore(ast.cls("!", "}", "-"), "}", "}"),
                ast.ignore(None, "}", ["}", "}"]),
                ast.subst(None, "}", "}", ast.gly_var("}", "start")),
                ast.subst(
                    ast.gly_var("}", "start"), "}", None, ast.gly_var("}", "end")
                ),
            ],
        ),
        ast.subst_liga(
            "{|",
            ign_prefix="{",
            ign_suffix=ast.cls("|", "}"),
        ),
        ast.subst_liga(
            "|}",
            ign_prefix=ast.cls("{", "|"),
            ign_suffix="}",
        ),
        ast.subst_liga(
            "{{--",
            ign_prefix="{",
            ign_suffix="-",
        ),
        ast.subst_liga(
            "{{!--",
            ign_prefix="{",
            ign_suffix="-",
        ),
        ast.subst_liga(
            "--}}",
            ign_prefix="-",
            ign_suffix="}",
        ),
    ]
