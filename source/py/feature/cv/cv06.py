import source.py.feature.ast as ast
from source.py.feature.cv.const import GLYPHS_I


def cv06_subst():
    return [
        ast.subst_map(
            GLYPHS_I,
            target_suffix=".cv06",
        ),
        ast.subst_map(
            GLYPHS_I,
            source_suffix=".cv03",
            target_suffix=".cv06",
        ),
    ]


cv06_name = "Alternative `i` without bottom bar, no effect on italic `i`"
cv06_feat_regular = ast.CharacterVariant(6, cv06_name, cv06_subst())
