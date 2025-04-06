from source.py.feature import ast


def ss05_subst():
    return [
        ast.subst(
            None,
            ast.gly("\\", ".liga"),
            None,
            "\\",
        )
    ]


ss05_name = "Revert thin backslash in escape symbols"
ss05_feat = ast.ss(5, ss05_name, ss05_subst())
