import source.py.feature.ast as ast
from source.py.feature.cv._common import GLYPHS_I


# https://github.com/subframe7536/maple-font/issues/324
def cv39_subst():
    def gen(*suffix_list: str):
        result: list[str] = []

        for suf in suffix_list:
            result.append(ast.gly("il", suf))
            result.append(ast.gly("ill", suf))

        return result

    return [
        ast.subst_map(
            GLYPHS_I,
            target_suffix=".cv39",
        ),
        ast.subst_map(
            GLYPHS_I,
            source_suffix=".cv33",
            target_suffix=".cv39",
        ),
        ast.subst_map(
            gen("", ".cv04", ".cv33", ".cv04.cv33", ".cv33.cv35"),
            target_suffix=".cv39",
        ),
    ]


cv39_name = "Alternative Italic `i` without bottom bar"
cv39_feat_italic = ast.CharacterVariant(
    id=39, desc=cv39_name, content=cv39_subst(), version="7.1", example="i"
)
