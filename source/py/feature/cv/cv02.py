import source.py.feature.ast as ast
from source.py.feature.cv.const import GLYPHS_A


def cv02_subst():
    return ast.subst_map(
        GLYPHS_A,
        target_suffix=".cv02",
    )


cv02_name = "Alternative `a` with top arm, no effect in italic style"
cv02_feat_regular = ast.CharacterVariant(2, cv02_name, cv02_subst())
