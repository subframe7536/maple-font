import source.py.feature.ast as ast
from source.py.feature.cv._common import GLYPHS_J_UPPER


# https://github.com/subframe7536/maple-font/issues/324
def cv07_subst():
    return [
        ast.subst_map(
            GLYPHS_J_UPPER,
            target_suffix=".cv07",
        ),
    ]


cv07_name = "Alternative `J` without top bar, no effect in italic style"
cv07_feat_regular = ast.CharacterVariant(
    id=7, desc=cv07_name, content=cv07_subst(), version="7.1", example="J"
)
