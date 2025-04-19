import source.py.feature.ast as ast


def cv63_subst():
    return [
        ast.subst_map(
            "<=",
            target_suffix=".cv63",
        ),
    ]


cv63_name = "Alternative `<=` in arrow style"
cv63_feat_regular = cv63_feat_italic = ast.CharacterVariant(63, cv63_name, cv63_subst())
