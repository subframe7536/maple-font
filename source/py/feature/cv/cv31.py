import source.py.feature.ast as ast
from source.py.feature.cv.const import GLYPHS_A


def cv31_subst():
    return ast.subst_map(
        [
            *GLYPHS_A,
            # Ligature variants
            ast.gly("al"),
            ast.gly("all"),
            ast.gly("al", ".cv04"),
            ast.gly("all", ".cv04"),
        ],
        target_suffix=".cv31",
    )


cv31_name = "Alternative italic `a` with top arm"
cv31_feat_italic = ast.CharacterVariant(31, cv31_name, cv31_subst())
