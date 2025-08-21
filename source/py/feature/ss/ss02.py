from source.py.feature import ast


def ss02_subst():
    return ast.subst_map(
        [
            "<=",
            ">=",
        ],
        target_suffix=".ss02",
    )


ss02_name = "Broken compare and equal ligatures (`<=`, `>=`)"
ss02_feat = ast.StylisticSet(
    id=2, desc=ss02_name, content=ss02_subst(), version="7.0", example=">="
)
