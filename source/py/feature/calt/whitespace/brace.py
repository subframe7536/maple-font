from source.py.feature import ast


def get_lookup():
    left_start = ast.gly_seq("{", "sta")
    left_end = ast.gly_seq("{", "end")
    right_start = ast.gly_seq("}", "sta")
    right_end = ast.gly_seq("}", "end")
    return [
        ast.Lookup(
            ast.gly("{{"),
            "{{",
            [
                ast.ign("{", "{", "{"),
                ast.ign(None, "{", ["{", ast.cls("{", "!", "-")]),
                ast.subst(None, "{", "{", left_start),
                ast.subst(left_start, "{", None, left_end),
            ],
        ),
        ast.Lookup(
            ast.gly("}}"),
            "}}",
            [
                ast.ign(ast.cls("!", "}", "-"), "}", "}"),
                ast.ign(None, "}", ["}", "}"]),
                ast.subst(None, "}", "}", right_start),
                ast.subst(right_start, "}", None, right_end),
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
