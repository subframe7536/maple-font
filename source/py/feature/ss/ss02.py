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
ss02_feat = ast.StylisticSet(2, ss02_name, ss02_subst())
