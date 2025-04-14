import source.py.feature.ast as ast
from source.py.feature.cv.const import GLYPHS_J_UPPER


def cv07_subst():
    return [
        ast.subst_map(
            GLYPHS_J_UPPER,
            target_suffix=".cv07",
        ),
    ]


cv07_name = "Alternative `J` without top bar, no effect on italic `J`"
cv07_feat_regular = ast.CharacterVariant(7, cv07_name, cv07_subst())
