from source.py.feature import ast
from source.py.feature.base.clazz import cls_question


def get_lookup():
    start = ast.gly_seq("#", "sta")
    mid = ast.gly_seq("#", "mid")
    end = ast.gly_seq("#", "end")
    return [
        ast.subst_liga(
            "__",
            ign_prefix=ast.cls("_", "#"),
            ign_suffix="_",
        ),
        ast.subst_liga(
            "#{",
            ign_prefix="#",
            ign_suffix="{",
        ),
        ast.subst_liga(
            "#[",
            ign_prefix="#",
            ign_suffix="[",
        ),
        ast.subst_liga(
            "#(",
            ign_prefix="#",
            ign_suffix="(",
        ),
        ast.subst_liga(
            [ast.gly("#"), cls_question.use()],
            target=ast.gly("#?"),
            desc="#?",
            ign_prefix="#",
            ign_suffix=cls_question,
        ),
        ast.subst_liga(
            "#!",
            ign_prefix="#",
            ign_suffix=ast.cls("!", "="),
        ),
        ast.subst_liga(
            "#:",
            ign_prefix="#",
            ign_suffix=ast.cls(":", "="),
        ),
        ast.subst_liga(
            "#=",
            ign_prefix="#",
            ign_suffix="=",
        ),
        ast.subst_liga(
            "#_",
            ign_suffix=ast.cls("_", "("),
        ),
        ast.subst_liga(
            "#__",
            ign_suffix="_",
        ),
        ast.subst_liga(
            "#_(",
            ign_suffix="(",
        ),
        ast.subst_liga(
            "]#",
            ign_prefix="]",
            ign_suffix="#",
        ),
        ast.Lookup(
            "infinite_numbersigns",
            "#######",
            [
                ast.subst(ast.cls(start, mid), "#", "#", mid),
                ast.subst(ast.cls(start, mid), "#", None, end),
                ast.subst(None, "#", "#", start),
            ],
        ),
    ]
