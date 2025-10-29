import source.py.feature.ast as ast
from source.py.feature.base.clazz import cls_uppercase


comb_top_acc = ast.Clazz(
    "CombiningTopAccents",
    [
        "acutecomb",
        "brevecomb",
        "caroncomb",
        "circumflexcomb",
        "commaturnedabovecomb",
        "dblgravecomb",
        "dieresiscomb",
        "dotaccentcomb",
        "gravecomb",
        "hookabovecomb",
        "hungarumlautcomb",
        "macroncomb",
        "ringcomb",
        "tildecomb",
    ],
)

comb_non_top_acc = ast.Clazz(
    "CombiningNonTopAccents",
    [
        "cedillacomb",
        "dotbelowcomb",
        "ogonekcomb",
        "ringbelowcomb",
        "horncomb",
        "slashlongcomb",
        "slashshortcomb",
        "strokelongcomb",
    ],
)

marks = [
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

marks_comb = ast.Clazz("Markscomb", marks)
marks_comb_case = ast.Clazz("MarkscombCase", [f"{m}.case" for m in marks])


def comb(c1: str, c2: str) -> list[ast.Line]:
    return [
        ast.__subst(f"{c1}comb {c2}comb", f"{c1}comb_{c2}comb"),
        ast.__subst(f"{c1}comb.case {c2}comb.case", f"{c1}comb_{c2}comb.case"),
    ]


def comb_jp(c1: str, c2: str) -> ast.Line:
    return ast.__subst(f"uni{c1} uni{c1}", f"uni{c1}{c2}")


ccmp_latn = ast.Lookup(
    "ccmp_latn",
    None,
    [
        ast.Line("lookupflag 0;"),
        comb("breve", "acute"),
        comb("breve", "grave"),
        comb("breve", "hookabove"),
        comb("breve", "tilde"),
        comb("circumflex", "acute"),
        comb("circumflex", "grave"),
        comb("circumflex", "hookabove"),
        comb("circumflex", "tilde"),
    ],
)
start_other = ast.cls("i", "i-cy", "iogonek", "idotbelow", "j", "je-cy")
end_other = ast.cls(
    "idotless",
    "idotless",
    "iogonekdotless",
    "idotbelowdotless",
    "jdotless",
    "jdotless",
)

ccmp_other_name = "ccmp_other"
ccmp_other = ast.Lookup(
    ccmp_other_name,
    None,
    [
        ast.subst(
            None,
            start_other,
            comb_top_acc,
            end_other,
        ),
        ast.subst(
            None,
            start_other,
            [comb_non_top_acc, comb_top_acc],
            end_other,
        ),
        ast.subst(marks_comb, marks_comb, None, marks_comb_case),
        ast.subst(cls_uppercase, marks_comb, None, marks_comb_case),
        ast.subst(None, marks_comb, marks_comb_case, marks_comb_case),
        ast.subst(marks_comb_case, marks_comb, None, marks_comb_case),
    ],
)

ccmp_jp = ast.Lookup(
    "ccmp_jp",
    None,
    [
        comb_jp("3042", "3099"),
        comb_jp("3044", "3099"),
        comb_jp("3048", "3099"),
        comb_jp("304A", "3099"),
        comb_jp("304B", "309A"),
        comb_jp("304D", "309A"),
        comb_jp("304F", "309A"),
        comb_jp("3051", "309A"),
        comb_jp("3053", "309A"),
        comb_jp("3093", "3099"),
        comb_jp("30A2", "3099"),
        comb_jp("30A4", "3099"),
        comb_jp("30A8", "3099"),
        comb_jp("30AA", "3099"),
        comb_jp("30AB", "309A"),
        comb_jp("30AD", "309A"),
        comb_jp("30AF", "309A"),
        comb_jp("30B1", "309A"),
        comb_jp("30B3", "309A"),
        comb_jp("30BB", "309A"),
        comb_jp("30C4", "309A"),
        comb_jp("30C8", "309A"),
        comb_jp("30F3", "3099"),
    ],
)

__ccmp = [
    ast.cls_states(
        comb_top_acc,
        comb_non_top_acc,
        marks_comb,
        marks_comb_case,
    ),
    ccmp_other,
    ccmp_latn,
    ast.script("latn"),
    ccmp_other.use(),
]


def get_ccmp_feature(cn: bool, cn_only: bool = False):
    if cn:
        content = ccmp_jp if cn_only else [__ccmp, ccmp_jp]
    else:
        content = __ccmp

    return ast.Feature("ccmp", content, "7.0")
