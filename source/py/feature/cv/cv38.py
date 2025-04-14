import source.py.feature.ast as ast
from source.py.feature.cv.const import GLYPHS_G


# https://github.com/subframe7536/maple-font/issues/329
def cv38_subst():
    return ast.subst_map(
        GLYPHS_G,
        target_suffix=".cv38",
    )


cv38_name = "Alternative italic `g` in double story style"
cv38_feat_italic = ast.CharacterVariant(38, cv38_name, cv38_subst())
