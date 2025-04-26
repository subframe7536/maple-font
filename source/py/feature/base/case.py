import source.py.feature.ast as ast


case_glyphs = [
    "colon",
    "periodcentered.loclCAT",
    "dieresiscomb",
    "dotaccentcomb",
    "gravecomb",
    "acutecomb",
    "hungarumlautcomb",
    "circumflexcomb",
    "caroncomb",
    "brevecomb",
    "ringcomb",
    "tildecomb",
    "macroncomb",
    "hookabovecomb",
    "dblgravecomb",
    "commaturnedabovecomb",
    "horncomb",
    "dotbelowcomb",
    "commaaccentcomb",
    "cedillacomb",
    "ogonekcomb",
    "dieresis",
    "dotaccent",
    "grave",
    "acute",
    "hungarumlaut",
    "circumflex",
    "caron",
    "breve",
    "ring",
    "tilde",
    "macron",
    "tonos",
    "brevecomb_acutecomb",
    "brevecomb_gravecomb",
    "brevecomb_hookabovecomb",
    "brevecomb_tildecomb",
    "circumflexcomb_acutecomb",
    "circumflexcomb_gravecomb",
    "circumflexcomb_hookabovecomb",
    "circumflexcomb_tildecomb",
]


def get_case_feature():
    return ast.Feature(
        "case",
        ast.subst_map(
            case_glyphs,
            target_suffix=".case",
        ),
        "7.0",
    )
