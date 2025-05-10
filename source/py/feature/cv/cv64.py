import source.py.feature.ast as ast


def cv64_subst():
    return [
        ast.subst_map(
            ["<=", ">="],
            target_suffix=".cv64",
        ),
    ]


cv64_name = "Alternative `<=` and `>=` with horizen bottom bar"
cv64_feat_regular = cv64_feat_italic = ast.CharacterVariant(
    id=64, desc=cv64_name, content=cv64_subst(), version="7.3", example="<="
)
