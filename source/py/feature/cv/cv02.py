import source.py.feature.ast as ast
from source.py.feature.cv._common import GLYPHS_A


def cv02_subst():
    return ast.subst_map(
        GLYPHS_A,
        target_suffix=".cv02",
    )


cv02_name = "Alternative `a` with top arm, no effect in italic style"
cv02_feat_regular = ast.CharacterVariant(
    id=2, desc=cv02_name, content=cv02_subst(), version="7.0", example="a"
)
