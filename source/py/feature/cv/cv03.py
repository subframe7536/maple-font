import source.py.feature.ast as ast
from source.py.feature.cv._common import GLYPHS_I


def cv03_subst():
    return ast.subst_map(
        GLYPHS_I,
        target_suffix=".cv03",
    )


cv03_name = "Alternative `i` without left bottom bar"
cv03_feat_regular = ast.CharacterVariant(
    id=3, desc=cv03_name, content=cv03_subst(), version="7.0", example="i"
)
