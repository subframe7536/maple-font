from source.py.feature import ast
from source.py.feature.calt.tag import built_in_tag_text


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
    for text in built_in_tag_text:
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
ss03_feat = ast.StylisticSet(
    id=3, desc=ss03_name, content=ss03_subst(), version="7.0", example="[info]"
)
