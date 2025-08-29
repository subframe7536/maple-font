import source.py.feature.ast as ast


i_acc = ast.__subst("i", "idotaccent")
locl_0 = ast.Lookup(
    "locl_latn_0",
    None,
    [
        ast.script("latn"),
        ast.lang("AZE"),
        i_acc,
        ast.lang("CRT"),
        i_acc,
        ast.lang("KAZ"),
        i_acc,
        ast.lang("TAT"),
        i_acc,
        ast.lang("TRK"),
        i_acc,
    ],
)

st_acc = ast.subst_map(
    ["S", "s", "T", "t"], source_suffix="cedilla", target_suffix="commaaccent"
)

locl_1 = ast.Lookup(
    "locl_latn_1",
    None,
    [
        ast.script("latn"),
        ast.lang("ROM"),
        st_acc,
        ast.lang("MOL"),
        st_acc,
    ],
)

glyph_2 = "periodcentered"

locl_2 = ast.Lookup(
    "locl_latn_2",
    None,
    [
        ast.script("latn"),
        ast.lang("CAT"),
        ast.subst(["l"], glyph_2, ["l"], f"{glyph_2}.loclCAT"),
        ast.subst(["L"], glyph_2, ["L"], f"{glyph_2}.loclCAT.case"),
    ],
)

locl_3 = ast.Lookup(
    "locl_latn_3",
    None,
    [
        ast.script("latn"),
        ast.lang("NLD"),
        ast.__subst("ij acutecomb", "ij_acute"),
        ast.__subst("IJ acutecomb", "IJ_acute"),
    ],
)


lookup_tw_name = "PunctuationTW"

# Must before all features
lookup_tw = ast.Lookup(
    lookup_tw_name,
    "Centered punctuations",
    ast.subst_map(
        [
            "uni3001",
            "uni3002",
            "uniFF01",
            "uniFF0C",
            "uniFF1A",
            "uniFF1B",
            "uniFF1F",
        ],
        target_suffix=".tw",
    ),
)

__locl = [
    locl_0,
    locl_1,
    locl_2,
    locl_3,
]

__locl_cn_only = [
    ast.lang("ZHH"),
    lookup_tw.use(),
    ast.lang("ZHT"),
    lookup_tw.use(),
]


def get_locl_feature_list(cn: bool, cn_only: bool = False):
    if not cn:
        return [ast.Feature("locl", __locl, "7.0")]

    content = __locl_cn_only if cn_only else __locl + __locl_cn_only
    return [lookup_tw, ast.Feature("locl", content, "7.0")]
