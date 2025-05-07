from source.py.feature import ast


def get_lookup():
    return [
        ast.subst_liga(
            "<>",
            ign_prefix="<",
            ign_suffix=">",
        ),
        ast.subst_liga(
            "</",
            ign_prefix="<",
            ign_suffix=ast.cls("/", ">"),
        ),
        ast.subst_liga(
            "/>",
            ign_prefix=ast.cls("<", "/"),
            ign_suffix=">",
        ),
        ast.subst_liga(
            "</>",
            ign_prefix="<",
            ign_suffix=">",
        ),
        ast.subst_liga(
            "<+",
            ign_prefix="<",
            ign_suffix=ast.cls("+", ">"),
        ),
        ast.subst_liga(
            "+>",
            ign_prefix=ast.cls("+", "<"),
            ign_suffix=">",
        ),
        ast.subst_liga(
            "<+>",
            ign_prefix="<",
            ign_suffix=">",
        ),
        ast.subst_liga(
            "<*",
            ign_prefix="<",
            ign_suffix=ast.cls("*", ">"),
        ),
        ast.subst_liga(
            "*>",
            ign_prefix=ast.cls("*", "<"),
            ign_suffix=">",
        ),
        ast.subst_liga(
            "<*>",
            ign_prefix="<",
            ign_suffix=">",
        ),
    ]
