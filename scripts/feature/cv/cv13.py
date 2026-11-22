import scripts.feature.ast as ast
from scripts.feature.cv._common import GLYPHS_Y_ALL


def cv13_subst():
    return ast.subst_map(GLYPHS_Y_ALL, target_suffix=".cv13")


cv13_name = "Alternative `y` in rounded style, no effect in italic style"
cv13_feat_regular = ast.CharacterVariant(
    id=13, desc=cv13_name, content=cv13_subst(), version="8.0", example="y"
)
