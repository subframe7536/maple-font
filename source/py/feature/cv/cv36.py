import source.py.feature.ast as ast


def cv36_subst():
    return ast.subst_map(
        [
            "x",
            "ha-cy",
            "hadescender-cy",
            "hahook-cy",
            "hastroke-cy",
            ast.gly("xl"),
            ast.gly("xl", ".cv04"),
            ast.gly("xl", ".cv35"),
        ],
        target_suffix=".cv36",
    )


cv36_name = "Alternative Italic `x` without top and bottom tails"
cv36_feat_italic = ast.CharacterVariant(
    id=36, desc=cv36_name, content=cv36_subst(), version="7.0", example="x"
)
