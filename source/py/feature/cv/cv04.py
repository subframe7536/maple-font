from source.py.feature import ast
from source.py.feature.cv._common import GLYPHS_L, GLYPHS_1


def cv04_subst_regular():
    return ast.subst_map(
        GLYPHS_L + GLYPHS_1,
        target_suffix=".cv04",
    )


def cv04_subst_italic():
    return ast.subst_map(
        [
            *GLYPHS_L,
            *GLYPHS_1,
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
cv04_feat_regular = ast.CharacterVariant(
    id=4, desc=cv04_name, content=cv04_subst_regular(), version="7.0", example="l1"
)
cv04_feat_italic = ast.CharacterVariant(
    id=4, desc=cv04_name, content=cv04_subst_italic(), version="7.0", example="l1"
)
