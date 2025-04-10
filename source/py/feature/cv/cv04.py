from source.py.feature import ast


cv04_base = [
    "l",
    "lacute",
    "lcaron",
    "lcommaaccent",
    "ldot",
    "lslash",
    "one",
    "one.dnom",
    "one.numr",
    "oneinferior",
    "onesuperior",
]


def cv04_subst_regular():
    return ast.subst_map(
        cv04_base,
        target_suffix=".cv04",
    )


def cv04_subst_italic():
    return ast.subst_map(
        [
            *cv04_base,
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
            ast.gly("ell"),
            ast.gly("ill"),
            ast.gly("ull"),
        ],
        target_suffix=".cv04",
    )

cv04_name = "Alternative `l` with left bottom bar, like consolas, will be overrided by `cv35` in italic style"
cv04_feat_regular = ast.CharacterVariant(4, cv04_name, cv04_subst_regular())
cv04_feat_italic = ast.CharacterVariant(4, cv04_name, cv04_subst_italic())
