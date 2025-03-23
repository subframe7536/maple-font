from fontTools.feaLib import ast as fea


def gly(g: str | fea.GlyphClassDefinition | list[str] | list[fea.GlyphClassDefinition]):
    if isinstance(g, list):
        return fea.GlyphClass([gly(x) for x in g])
    if isinstance(g, fea.GlyphClassDefinition):
        return g
    return fea.GlyphName(g)


def cls(name: str, glyphs: list[str]):
    return fea.GlyphClassDefinition(
        name=name,
        glyphs=fea.GlyphClass([fea.GlyphName(glyph) for glyph in glyphs]),
    )


def parse_glyphs_array(
    data: str
    | fea.GlyphClassDefinition
    | list[str]
    | list[fea.GlyphClassDefinition]
    | None,
):
    if isinstance(data, list):
        return [gly(g) for g in data]
    if not data:
        return []
    return [gly(data)]


def subst(
    glyphs: str | fea.GlyphClassDefinition | list[str] | list[fea.GlyphClassDefinition],
    replace: str,
    prefix: str
    | fea.GlyphClassDefinition
    | list[str]
    | list[fea.GlyphClassDefinition]
    | None = None,
    suffix: str
    | fea.GlyphClassDefinition
    | list[str]
    | list[fea.GlyphClassDefinition]
    | None = None,
):
    return fea.SingleSubstStatement(
        glyphs=parse_glyphs_array(glyphs),
        replace=[gly(replace)],
        prefix=parse_glyphs_array(prefix),
        suffix=parse_glyphs_array(suffix),
        forceChain=False,
    )


def lkup(name: str, data: list[fea.SingleSubstStatement] | None = None):
    lookup = fea.LookupBlock(name=name)
    if data:
        lookup.statements.extend(data)
    return lookup


def blk(
    name: str,
    data: list[fea.LookupBlock] | list[fea.SingleSubstStatement] | None = None,
):
    block = fea.FeatureBlock(name=name)
    if data:
        block.statements.extend(data)
    return block


def create_fea(classes: list[fea.GlyphClassDefinition], blocks: list[fea.FeatureBlock]):
    fea_file = fea.FeatureFile()
    fea_file.statements.extend(classes)
    fea_file.statements.extend(blocks)
    return fea_file
