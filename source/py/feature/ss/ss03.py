from collections.abc import Sequence
from source.py.feature import ast


__map = {
    ">": "sharp_right.bg",
    "<": "sharp_left.bg",
    ")": "circle_right.bg",
    "(": "circle_left.bg",
    "[": "base.bg",
    "]": "base.bg",
}


def badge(content: str | Sequence[str | ast.Clazz], target: str):
    """
    Generate OpenType feature file substitutions for a given content and target.

    Args:
        content (str): The input sequence of glyphs (e.g., '[todo]', 'todo))').
        target (str): The target string defining the letter variants (e.g., 'todo', 'warn').

    Returns:
        list[str]: A list of substitution rules in OpenType feature file format.
    """
    # Split content into individual glyphs
    glyphs = list(content)
    glyphs_len = len(glyphs)  # Total length of the content
    target_len = len(target)  # Number of letters in the target

    if target_len + 2 != glyphs_len:
        raise ValueError(
            f"Content length ({glyphs_len}) must be equal to target length ({target_len}) + 2."
        )

    glyph_reps = []
    for g in glyphs:
        if isinstance(g, ast.Clazz):
            glyph_reps.append(g)
        elif g.isalpha():
            glyph_reps.append(f"@{g.upper()}")
        else:
            glyph_reps.append(ast.gly(g))

    target_list = [
        __map["["],
        *[f"{t.upper()}.bg" for t in target],
        __map[")"],
    ]

    # Generate substitutions in reverse order (from last glyph to first)
    result = []
    for i in range(glyphs_len, 0, -1):
        before = target_list[: i - 1]
        after = glyph_reps[i:] if i < glyphs_len else None
        source = glyph_reps[i - 1]
        replacement = target_list[i - 1]
        result.append(ast.subst(before, source, after, replacement))

    return ast.Lookup(name=f"custom_badge_{target}", desc=target, content=result)


# print(ast.create([badge("(todo:", "todo")]))


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
        # liga_cls("todo"),
        badge("[todo)", "todo"),
        liga_cls("fixme"),
    ]


ss03_name = "Allow to use any case in all tags"
ss03_feat = ast.StylisticSet(3, ss03_name, ss03_subst())
