import scripts.feature.ast as ast

# East Asian Width "Ambiguous" glyphs default to half width so terminals that
# treat them as single cells do not overlap; this variant restores full width.
ROMAN_NUMERAL_CODEPOINTS = [*range(0x2160, 0x216C), *range(0x2170, 0x217C)]
ENCLOSED_ALPHANUMERIC_CODEPOINTS = range(0x2460, 0x2500)
CIRCLED_NUMBER_ON_SQUARE_CODEPOINTS = range(0x3248, 0x3250)


def cv95_subst():
    return ast.subst_map(
        [
            f"uni{codepoint:04X}"
            for codepoints in (
                ROMAN_NUMERAL_CODEPOINTS,
                ENCLOSED_ALPHANUMERIC_CODEPOINTS,
                CIRCLED_NUMBER_ON_SQUARE_CODEPOINTS,
            )
            for codepoint in codepoints
        ],
        target_suffix=".full",
    )


cv95_name = "Full width Roman numerals and enclosed alphanumerics (`Ⅻ` / `①` / `ⓐ`)"
cv95_feat_cn = ast.CharacterVariant(
    id=95, desc=cv95_name, content=cv95_subst(), version="8.0", example="Ⅻ①ⓐ"
)
