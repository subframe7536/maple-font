import source.py.feature.ast as ast


def cv44_subst():
    return [
        *ast.subst_map(["f", ast.gly("ff")], target_suffix=".cv44"),
        *ast.subst_map(
            ["f", ast.gly("ff")], source_suffix=".cv32", target_suffix=".cv44"
        ),
    ]


cv44_name = "Alternative Italic `f` with bottom bar"
cv44_feat_italic = ast.CharacterVariant(
    id=44, desc=cv44_name, content=cv44_subst(), version="7.7", example="f"
)
