import scripts.feature.ast as ast


def cv69_subst():
    # Reuse the `.cv01` glyphs extracted from cv01.
    return ast.subst_map(["@", "~@"], target_suffix=".cv01")


cv69_name = "Normalize `@`"
cv69_feat = ast.CharacterVariant(
    id=69, desc=cv69_name, content=cv69_subst(), version="8.0", example="@"
)
