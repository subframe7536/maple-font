from source.py.feature import ast


def ss06_subst():
    # Only handle glyphs that contains:
    # - default letter & default `l`
    # - default `ll`
    # - `ff`
    # - `tt`
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
            ast.gly("ill", ".cv39"),
            ast.gly("ill", ".cv33.cv39"),
            ast.gly("ull"),
            ast.gly("ff"),
            ast.gly("ff", ".cv32"),
            ast.gly("ff", ".cv44"),
            ast.gly("tt"),
        ],
        target_suffix=".ss06",
    )


ss06_name = "Break connected strokes between italic letters (`al`, `il`, `ull` ...)"
ss06_feat = ast.StylisticSet(
    id=6, desc=ss06_name, content=ss06_subst(), version="7.0", example="all"
)
