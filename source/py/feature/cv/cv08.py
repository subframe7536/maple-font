import source.py.feature.ast as ast
from source.py.feature.cv._common import GLYPHS_R


# https://github.com/subframe7536/maple-font/issues/328
def cv08_subst():
    return [
        ast.subst_map(
            GLYPHS_R,
            target_suffix=".cv08",
        ),
    ]


cv08_name = "Alternative `r` with bottom bar, no effect in italic style"
cv08_feat_regular = ast.CharacterVariant(
    id=8, desc=cv08_name, content=cv08_subst(), version="7.1", example="r"
)
