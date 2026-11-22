import scripts.feature.ast as ast
from scripts.feature.cv._common import GLYPHS_I


def cv33_subst():
    def gen(*suffix_list: str):
        result: list[str] = []

        for suf in suffix_list:
            result.append(ast.gly("il", suf))
            result.append(ast.gly("ill", suf))

        return result

    return [
        ast.subst_map(
            [
                *GLYPHS_I,
                "j",
                "jcircumflex",
                "jdotless",
                "je-cy",
                *gen(""),
            ],
            target_suffix=".cv33",
        ),
        ast.subst_map(
            gen(""),
            source_suffix=".cv46",
            target_suffix=".cv33.cv46",
        ),
    ]


cv33_name = "Alternative Italic `i` and `j` with left bottom bar and horizen top bar"
cv33_feat_italic = ast.CharacterVariant(
    id=33, desc=cv33_name, content=cv33_subst(), version="7.0", example="i"
)
