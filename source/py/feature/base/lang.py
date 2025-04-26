import source.py.feature.ast as ast


def get_lang_list():
    return [
        ast.Line(""),
        ast.langsys("DFLT", "dflt"),
        ast.Line(""),
        ast.langsys("latn", "dflt"),
        ast.langsys("latn", "AZE"),
        ast.langsys("latn", "CRT"),
        ast.langsys("latn", "KAZ"),
        ast.langsys("latn", "TAT"),
        ast.langsys("latn", "TRK"),
        ast.langsys("latn", "ROM"),
        ast.langsys("latn", "MOL"),
        ast.langsys("latn", "CAT"),
    ]
