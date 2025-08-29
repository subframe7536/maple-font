from source.py.feature import ast
from source.py.feature.base.clazz import cls_comma


def get_lookup():
    return [
        ast.subst_liga(
            "<|||",
            ign_prefix="<",
            ign_suffix=ast.cls("|", ">"),
        ),
        ast.subst_liga(
            "|||>",
            ign_prefix="|",
            ign_suffix=">",
        ),
        ast.subst_liga(
            "<||",
            ign_prefix="<",
            ign_suffix=ast.cls("|", ">"),
        ),
        ast.subst_liga(
            "||>",
            ign_prefix=ast.cls("-", "<"),
            ign_suffix=">",
        ),
        ast.subst_liga(
            "<|",
            ign_prefix="<",
            ign_suffix=ast.cls("|", ">"),
        ),
        ast.subst_liga(
            "|>",
            ign_prefix=ast.cls("-", "<", "|"),
            ign_suffix=ast.cls(">", "="),
        ),
        ast.subst_liga(
            "<|>",
            ign_prefix="<",
            ign_suffix=">",
        ),
        ast.subst_liga(
            "_|_",
            ign_prefix=ast.cls("_", "[", cls_comma),
            ign_suffix="_",
        ),
    ]
