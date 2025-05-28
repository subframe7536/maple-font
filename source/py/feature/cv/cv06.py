import source.py.feature.ast as ast
from source.py.feature.cv._common import GLYPHS_I


# https://github.com/subframe7536/maple-font/issues/324
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


cv06_name = "Alternative `i` without bottom bar, no effect in italic style"
cv06_feat_regular = ast.CharacterVariant(
    id=6, desc=cv06_name, content=cv06_subst(), version="7.1", example="i"
)
