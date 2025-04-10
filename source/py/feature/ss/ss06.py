from source.py.feature import ast


def ss06_subst():
    return ast.subst_map(
        [
            ast.gly("Cl"),
            ast.gly("al"),
            ast.gly("cl"),
            ast.gly("el"),
            ast.gly("il"),
            ast.gly("ll"),
            ast.gly("tl"),
            ast.gly("ul"),
            ast.gly("xl"),
            ast.gly("all"),
            ast.gly("all", ".cv31"),
            ast.gly("ell"),
            ast.gly("ill"),
            ast.gly("ill", ".cv33"),
            ast.gly("ull"),
            ast.gly("ff"),
            ast.gly("ff", ".cv32"),
            ast.gly("tt"),
        ],
        target_suffix=".ss06",
    )


ss06_name = "Break connected strokes between italic letters (`al`, `il`, `ull` ...)"
ss06_feat = ast.StylisticSet(6, ss06_name, ss06_subst())
