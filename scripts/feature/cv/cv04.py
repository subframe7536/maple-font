from scripts.feature import ast
from scripts.feature.cv._common import GLYPHS_1, GLYPHS_L


def cv04_subst():
    return ast.subst_map(
        GLYPHS_L + GLYPHS_1,
        target_suffix=".cv04",
    )


cv04_name = "Alternative `l` with left bottom bar, like consolas"
cv04_feat_regular = ast.CharacterVariant(
    id=4, desc=cv04_name, content=cv04_subst(), version="7.0", example="l1"
)
