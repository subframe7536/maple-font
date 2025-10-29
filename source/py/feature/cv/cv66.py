import source.py.feature.ast as ast


def cv66_subst():
    glyphs = ["||>", "<||", "<|", "|>", "<|>", "|||>", "<|||"]
    return [
        ast.subst_map(
            glyphs,
            target_suffix=".cv66",
        ),
    ]


cv66_name = "Alternative pipe arrows"
cv66_feat = ast.CharacterVariant(
    id=66, desc=cv66_name, content=cv66_subst(), version="7.8", example="|>"
)
