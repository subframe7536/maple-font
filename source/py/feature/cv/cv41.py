import source.py.feature.ast as ast
from source.py.feature.cv.const import GLYPHS_R


# https://github.com/subframe7536/maple-font/issues/328
def cv41_subst():
    return [
        ast.subst_map(
            GLYPHS_R,
            target_suffix=".cv41",
        ),
    ]


cv41_name = "Alternative italic `r` with bottom bar"
cv41_feat_italic = ast.CharacterVariant(41, cv41_name, cv41_subst())
