import source.py.feature.ast as ast
from source.py.feature.cv.const import GLYPHS_G


# https://github.com/subframe7536/maple-font/issues/329
def cv05_subst():
    return ast.subst_map(
        GLYPHS_G,
        target_suffix=".cv05",
    )


cv05_name = "Alternative `g` in double story style, no effect in italic style"
cv05_feat_regular = ast.CharacterVariant(5, cv05_name, cv05_subst())
