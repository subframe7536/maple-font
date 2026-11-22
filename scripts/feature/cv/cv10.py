import scripts.feature.ast as ast
from scripts.feature.cv._common import GLYPHS_Z_ALL


# https://github.com/subframe7536/maple-font/issues/549
def cv10_subst():
    return [
        ast.subst_map(
            GLYPHS_Z_ALL,
            target_suffix=".cv10",
        ),
    ]


cv10_name = "Alternative `Z` and `z` with middle bar, no effect in italic style"
cv10_feat_regular = ast.CharacterVariant(
    id=10, desc=cv10_name, content=cv10_subst(), version="7.5", example="Zz"
)
