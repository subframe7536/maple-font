import source.py.feature.ast as ast
from source.py.feature.cv.const import GLYPHS_I


def cv03_subst():
    return ast.subst_map(
        GLYPHS_I,
        target_suffix=".cv03",
    )


cv03_name = "Alternative `i` without left bottom bar"
cv03_feat_regular = ast.CharacterVariant(3, cv03_name, cv03_subst())
