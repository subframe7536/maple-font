import source.py.feature.ast as ast


def cv65_subst():
    glyphs = ["&", "&&", "&&&"]
    return [
        ast.subst_map(
            glyphs,
            target_suffix=".cv65",
        ),
        ast.subst_map(
            glyphs,
            source_suffix=".cv01",
            target_suffix=".cv65",
        ),
    ]


cv65_name = "Alternative `&` in handwriting style"
cv65_feat_regular = cv65_feat_italic = ast.CharacterVariant(
    id=65, desc=cv65_name, content=cv65_subst(), version="7.3", example="&"
)
