from source.py.feature import ast


def ss04_subst():
    return ast.subst_map(
        [
            "__",
            "#__",
        ],
        target_suffix=".ss04",
    )


ss04_name = "Broken multiple underscores ligatures (`__`, `#__`)"
ss04_feat = ast.StylisticSet(
    id=4, desc=ss04_name, content=ss04_subst(), version="7.0", example="__"
)
