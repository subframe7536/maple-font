import scripts.feature.ast as ast
from scripts.feature.cv._common import GLYPHS_Z_ALL


# https://github.com/subframe7536/maple-font/issues/549
def cv43_subst():
    return [
        ast.subst_map(
            GLYPHS_Z_ALL,
            target_suffix=".cv43",
        ),
    ]


cv43_name = "Alternative italic `Z` and `z` with middle bar"
cv43_feat_italic = ast.CharacterVariant(
    id=43, desc=cv43_name, content=cv43_subst(), version="7.5", example="Zz"
)
