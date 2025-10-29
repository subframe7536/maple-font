import source.py.feature.ast as ast
from source.py.feature.cv._common import GLYPHS_7


# https://github.com/subframe7536/maple-font/issues/549
def cv09_subst():
    return [
        ast.subst_map(
            GLYPHS_7,
            target_suffix=".cv09",
        ),
    ]


cv09_name = "Alternative `7` with middle bar, no effect in italic style"
cv09_feat_regular = ast.CharacterVariant(
    id=9, desc=cv09_name, content=cv09_subst(), version="7.5", example="7"
)
