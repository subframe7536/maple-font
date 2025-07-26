import source.py.feature.ast as ast
from source.py.feature.cv._common import GLYPHS_7


# https://github.com/subframe7536/maple-font/issues/549
def cv42_subst():
    return [
        ast.subst_map(
            GLYPHS_7,
            target_suffix=".cv42",
        ),
    ]


cv42_name = "Alternative italic `7` with middle bar"
cv42_feat_italic = ast.CharacterVariant(
    id=42, desc=cv42_name, content=cv42_subst(), version="7.5", example="7"
)
