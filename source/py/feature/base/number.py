import source.py.feature.ast as ast

_number_list = [
    "zero",
    "one",
    "two",
    "three",
    "four",
    "five",
    "six",
    "seven",
    "eight",
    "nine",
]
clazz_number = ast.cls(_number_list)
clazz_numr = ast.cls([f"{n}.numr" for n in _number_list])
clazz_dnom = ast.cls([f"{n}.dnom" for n in _number_list])

zero = ast.subst_map(
    ["zero", "zero.dnom", "zero.numr", "zeroinferior", "zerosuperior"],
    target_suffix=".zero",
)

sinf = ast.subst_map(_number_list, target_suffix="inferior")
# subs is same as sinf, use another instance to correct indent
subs = ast.subst_map(_number_list, target_suffix="inferior")
sups = ast.subst_map(_number_list, target_suffix="superior")
numr = ast.subst_map(_number_list, target_suffix=".numr")
dnom = ast.subst_map(_number_list, target_suffix=".dnom")
ordn = [
    ast.subst(clazz_number, ast.cls("A", "a"), None, "ordfeminine"),
    ast.subst(clazz_number, ast.cls("O", "o"), None, "ordmasculine"),
    ast.__subst("N o period", "numero"),
]

frac = [
    ast.Lookup("FRAC", None, [ast.subst(None, "/", None, "fraction")]),
    ast.Lookup(
        "UP",
        None,
        [ast.subst(None, clazz_number, None, clazz_numr)],
    ),
    ast.Lookup(
        "DOWN",
        None,
        [
            ast.subst("fraction", clazz_numr, None, clazz_dnom),
            ast.subst(
                clazz_dnom,
                clazz_numr,
                None,
                clazz_dnom,
            ),
        ],
    ),
]

number_features = [
    ast.Feature("sinf", sinf),
    ast.Feature("subs", subs),
    ast.Feature("sups", sups),
    ast.Feature("numr", numr),
    ast.Feature("dnom", dnom),
    ast.Feature("frac", frac),
    ast.Feature("ordn", ordn),
    ast.Feature("zero", zero),
]
