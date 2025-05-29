from source.py.feature import ast


def get_lookup():
    start = ast.gly_seq("~", "sta")
    mid = ast.gly_seq("~", "mid")
    end = ast.gly_seq("~", "end")
    return [
        ast.subst_liga(
            "<~",
            ign_prefix="<",
            ign_suffix=ast.cls("~", ">"),
        ),
        ast.subst_liga(
            "~>",
            ign_prefix=ast.cls("~", "<"),
            ign_suffix=">",
        ),
        ast.subst_liga(
            "~~",
            ign_prefix=ast.cls("~", "<"),
            ign_suffix=ast.cls("~", ">"),
        ),
        ast.subst_liga(
            "<~>",
            ign_prefix="<",
            ign_suffix=">",
        ),
        ast.subst_liga(
            "<~~",
            ign_prefix="<",
            ign_suffix=ast.cls("~", ">"),
        ),
        ast.subst_liga(
            "~~>",
            ign_prefix=ast.cls("~", "<"),
            ign_suffix=">",
        ),
        ast.subst_liga(
            "-~",
            ign_prefix="-",
            ign_suffix="~",
        ),
        ast.subst_liga(
            "~-",
            ign_prefix="~",
            ign_suffix="-",
        ),
        ast.subst_liga(
            "~@",  # Cloujure
            ign_prefix="~",
            ign_suffix="@",
        ),
        ast.Lookup(
            "infinite_asciitilde",
            "~~~~~~~",
            [
                ast.subst(ast.cls(start, mid), "~", "~", mid),
                ast.subst(ast.cls(start, mid), "~", None, end),
                ast.subst(None, "~", "~", start),
            ],
        ),
    ]
