import scripts.feature.ast as ast
from scripts.feature.cv._common import GLYPHS_A


def cv31_subst():
    return [
        ast.subst_map(
            [
                *GLYPHS_A,
                # Ligature variants
                ast.gly("al"),
                ast.gly("all"),
            ],
            target_suffix=".cv31",
        ),
        ast.subst_map(
            [
                ast.gly("al"),
                ast.gly("all"),
            ],
            source_suffix=".cv46",
            target_suffix=".cv31.cv46",
        ),
    ]


cv31_name = "Alternative italic `a` with top arm"
cv31_feat_italic = ast.CharacterVariant(
    id=31, desc=cv31_name, content=cv31_subst(), version="7.0", example="a"
)
