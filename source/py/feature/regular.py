import source.py.feature.ast as ast
from source.py.feature.base import get_base_features
from source.py.feature.calt import get_calt
from source.py.feature.cv import cv01, cv02, cv03, cv04, cv96, cv97, cv98, cv99
from source.py.feature.ss import ss01, ss02, ss03, ss04, ss05, ss07, ss08
from source.py.feature.base.clazz import base_class_list, digit
from source.py.feature.base.lang import lang_list


cls_a = ast.Clazz("A", ["A", "a", "a.cv02"])
cls_b = ast.Clazz("B", ["B", "b"])
cls_c = ast.Clazz("C", ["C", "c"])
cls_d = ast.Clazz("D", ["D", "d"])
cls_e = ast.Clazz("E", ["E", "e"])
cls_f = ast.Clazz("F", ["F", "f"])
cls_g = ast.Clazz("G", ["G", "g"])
cls_h = ast.Clazz("H", ["H", "h"])
cls_i = ast.Clazz("I", ["I", "i", "i.cv03"])
cls_j = ast.Clazz("J", ["J", "j"])
cls_k = ast.Clazz("K", ["K", "k"])
cls_l = ast.Clazz("L", ["L", "l", "l.cv04"])
cls_m = ast.Clazz("M", ["M", "m"])
cls_n = ast.Clazz("N", ["N", "n"])
cls_o = ast.Clazz("O", ["O", "o"])
cls_p = ast.Clazz("P", ["P", "p"])
cls_q = ast.Clazz("Q", ["Q", "q", "Q.cv01"])
cls_r = ast.Clazz("R", ["R", "r"])
cls_s = ast.Clazz("S", ["S", "s"])
cls_t = ast.Clazz("T", ["T", "t"])
cls_u = ast.Clazz("U", ["U", "u"])
cls_v = ast.Clazz("V", ["V", "v"])
cls_w = ast.Clazz("W", ["W", "w"])
cls_x = ast.Clazz("X", ["X", "x"])
cls_y = ast.Clazz("Y", ["Y", "y"])
cls_z = ast.Clazz("Z", ["Z", "z"])
cls_hex_letter = ast.Clazz("HexLetter", [cls_a, cls_b, cls_c, cls_d, cls_e, cls_f])

cls_letters_list = [
    cls_a,
    cls_b,
    cls_c,
    cls_d,
    cls_e,
    cls_f,
    cls_g,
    cls_h,
    cls_i,
    cls_j,
    cls_k,
    cls_l,
    cls_m,
    cls_n,
    cls_o,
    cls_p,
    cls_q,
    cls_r,
    cls_s,
    cls_t,
    cls_u,
    cls_v,
    cls_w,
    cls_x,
    cls_y,
    cls_z,
]

cls_var = ast.Clazz("Var", ["_", "__", *cls_letters_list, digit])

class_list_regular = [*base_class_list, *cls_letters_list, cls_hex_letter, cls_var]

calt_regular = get_calt(cls_var, cls_hex_letter, is_italic=False)

cv_list_regular = [
    cv01.cv01_feat_regular,
    cv02.cv02_feat_regular,
    cv03.cv03_feat_regular,
    cv04.cv04_feat_regular,
]


cv_list_cn = [
    cv96.cv96_feat_cn,
    cv97.cv97_feat_cn,
    cv98.cv98_feat_cn,
    cv99.cv99_feat_cn,
]


ss_list_regular = [
    ss01.ss01_feat,
    ss02.ss02_feat,
    ss03.ss03_feat,
    ss04.ss04_feat,
    ss05.ss05_feat,
    ss07.ss07_feat,
    ss08.ss08_feat,
]


feature_file_regular = ast.create(
    [
        class_list_regular,
        lang_list,
        get_base_features(calt_regular, False),
        cv_list_regular,
        ss_list_regular,
    ],
)

feature_file_regular_cn = ast.create(
    [
        class_list_regular,
        lang_list,
        get_base_features(calt_regular, True),
        cv_list_regular,
        cv_list_cn,
        ss_list_regular,
    ],
)
