from source.py.feature import ast


def liga_cls(text: str):
    # There are many classes for letters, allows to use letters in any case
    # e.g. `@I @N @F @O` matches:
    #   - INFO
    #   - INFo
    #   - INfO
    #   - INfo
    #   - InFO
    #   - InFo
    #   - InfO
    #   - Info
    #   - iNFO
    #   - iNFo
    #   - iNfO
    #   - iNfo
    #   - inFO
    #   - inFo
    #   - infO
    #   - info
    arr = ["["] + [f"@{g.upper()}" for g in text] + ["]"]
    return ast.subst_liga(
        arr,
        target=f"badge_{text}.liga",
        lookup_name=f"badge_{text}.liga.ss03",
        desc=f"[{text}]",
    )


def ss03_subst():
    return [
        liga_cls("trace"),
        liga_cls("debug"),
        liga_cls("info"),
        liga_cls("warn"),
        liga_cls("error"),
        liga_cls("fatal"),
        liga_cls("todo"),
        liga_cls("fixme"),
    ]


ss03_name = "Allow to use any case in all tags"
ss03_feat = ast.StylisticSet(3, ss03_name, ss03_subst())
