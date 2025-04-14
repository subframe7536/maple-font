import source.py.feature.ast as ast
from source.py.feature.cv.const import GLYPHS_J_UPPER


# https://github.com/subframe7536/maple-font/issues/324
def cv40_subst():
    return [
        ast.subst_map(
            GLYPHS_J_UPPER,
            target_suffix=".cv40",
        ),
    ]


cv40_name = "Alternative italic `J` without top bar"
cv40_feat_italic = ast.CharacterVariant(40, cv40_name, cv40_subst())
