import source.py.feature.ast as ast


def cv35_subst():
    base_glyphs = [
        "l",
        "lacute",
        "lcaron",
        "lcommaaccent",
        "ldot",
        "lslash",
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

    result.append([ast.subst(None, "one.cv04", None, "one")])

    return result


cv35_name = "Alternative Italic `l` without center tail"
cv35_feat_italic = ast.CharacterVariant(35, cv35_name, cv35_subst())
