import source.py.feature.ast as ast
from source.py.feature.cv._common import GLYPHS_I


def cv33_subst():
    def gen(*suffix_list: str):
        result: list[str] = []

        for suf in suffix_list:
            result.append(ast.gly("il", suf))
            result.append(ast.gly("ill", suf))

        return result

    return ast.subst_map(
        [
            *GLYPHS_I,
            "j",
            "jcircumflex",
            "jdotless",
            "je-cy",
            *gen("", ".cv04"),
        ],
        target_suffix=".cv33",
    )


cv33_name = "Alternative Italic `i` and `j` with left bottom bar and horizen top bar"
cv33_feat_italic = ast.CharacterVariant(
    id=33, desc=cv33_name, content=cv33_subst(), version="7.0", example="i"
)
