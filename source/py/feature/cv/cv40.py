import source.py.feature.ast as ast
from source.py.feature.cv._common import GLYPHS_J_UPPER


# https://github.com/subframe7536/maple-font/issues/324
def cv40_subst():
    return [
        ast.subst_map(
            GLYPHS_J_UPPER,
            target_suffix=".cv40",
        ),
    ]


cv40_name = "Alternative italic `J` without top bar"
cv40_feat_italic = ast.CharacterVariant(
    id=40, desc=cv40_name, content=cv40_subst(), version="7.1", example="J"
)
