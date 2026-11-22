import scripts.feature.ast as ast
from scripts.feature.cv._common import GLYPHS_1, GLYPHS_L


def cv46_subst():
    ligas = [
        ast.gly("Cl"),
        ast.gly("al"),
        ast.gly("cl"),
        ast.gly("el"),
        ast.gly("il"),
        ast.gly("ll"),
        ast.gly("tl"),
        ast.gly("ul"),
        ast.gly("xl"),
        ast.gly("all"),
        ast.gly("ell"),
        ast.gly("ill"),
        ast.gly("ull"),
    ]

    result = ast.subst_map(
        [
            *GLYPHS_L,
            *GLYPHS_1,
            *ligas,
        ],
        target_suffix=".cv46",
    )

    # Earlier character variants may have substituted these glyphs; cv46 takes precedence over cv35.
    chained = [
        (".cv35", ".cv46", [g for g in GLYPHS_L if g != "lslash"] + ligas),
        (".cv31", ".cv31.cv46", [ast.gly("al"), ast.gly("all")]),
        (".cv33", ".cv33.cv46", [ast.gly("il"), ast.gly("ill")]),
        (".cv36", ".cv36.cv46", [ast.gly("xl")]),
        (".cv39", ".cv39.cv46", [ast.gly("il"), ast.gly("ill")]),
        (".cv33.cv39", ".cv33.cv39.cv46", [ast.gly("il"), ast.gly("ill")]),
        (".cv31.cv35", ".cv31.cv46", [ast.gly("al"), ast.gly("all")]),
        (".cv33.cv35", ".cv33.cv46", [ast.gly("il"), ast.gly("ill")]),
        (".cv35.cv36", ".cv36.cv46", [ast.gly("xl")]),
        (".cv33.cv35.cv39", ".cv33.cv39.cv46", [ast.gly("il"), ast.gly("ill")]),
    ]
    for source_suffix, target_suffix, glyphs in chained:
        result += ast.subst_map(
            glyphs,
            source_suffix=source_suffix,
            target_suffix=target_suffix,
        )

    return result


cv46_name = "Alternative italic `l` with left bottom bar, like consolas"
cv46_feat_italic = ast.CharacterVariant(
    id=46, desc=cv46_name, content=cv46_subst(), version="8.0", example="l1"
)
