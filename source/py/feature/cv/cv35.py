import source.py.feature.ast as ast
from source.py.feature.cv._common import GLYPHS_L, GLYPHS_1


def cv35_subst():
    base_glyphs = [
        *[g for g in GLYPHS_L if g != 'lslash'],
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

    # previous cv
    overwrite_glyphs = {
        ast.gly("al"): ".cv31",
        ast.gly("all"): ".cv31",
        ast.gly("il"): ".cv33",
        ast.gly("ill"): ".cv33",
    }

    suf_cv04 = ".cv04"
    suf_cv35 = ".cv35"

    result = [
        ast.subst_map(base_glyphs, target_suffix=suf_cv35),
        ast.subst_map(
            base_glyphs,
            source_suffix=suf_cv04,
            target_suffix=suf_cv35,
        ),
    ]

    for liga, suf in overwrite_glyphs.items():
        result.extend(
            [
                # overwrite
                ast.subst_map(f"{liga}{suf}", target_suffix=suf_cv35),
                ast.subst_map(
                    liga,
                    source_suffix=f"{suf_cv04}{suf}",
                    target_suffix=f"{suf}{suf_cv35}",
                ),
            ]
        )

    result += ast.subst_map(GLYPHS_1, source_suffix=".cv04")

    return result


cv35_name = "Alternative Italic `l` without center tail"
cv35_feat_italic = ast.CharacterVariant(
    id=35, desc=cv35_name, content=cv35_subst(), version="7.0", example="l"
)
