from source.py.feature import ast
from source.py.feature.calt.tag import upper_tag_text


def ss03_subst():
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
    result = []
    for text in upper_tag_text:
        arr = ["["] + [f"@{g.upper()}" for g in text] + ["]"]
        result.append(
            ast.subst_liga(
                arr,
                target=f"tag_{text}.liga",
                lookup_name=f"tag_{text}.liga.ss03",
                desc=f"[{text}]",
            )
        )
    return result


ss03_name = "Allow to use any case in all tags"
ss03_feat = ast.StylisticSet(3, ss03_name, ss03_subst())
