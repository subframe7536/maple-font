from collections.abc import Sequence
from source.py.feature import ast


def tag_upper(text_list: list[str]):
    result = []

    for text in text_list:
        source = ["["] + [g.upper() for g in text] + ["]"]
        result.append(
            ast.subst_liga(
                source,
                target=f"badge_{text}.liga",
                lookup_name=f"badge_{text}",
                desc="".join(source),
            )
        )

    return result


def tag_any(text_list: list[str], cls_var: ast.Clazz):
    result = []

    for text in text_list:
        glyphs_first = f"@{text[0].upper()}"
        glyphs_rest = [f"@{g.upper()}" for g in text[1:]] + [")", ")"]
        result.append(
            ast.subst_liga(
                [glyphs_first] + glyphs_rest,
                target=f"badge_{text}.liga",
                lookup_name=f"badge_{text}_alt",
                desc=f"{text}))",
                banner=[ast.ignore(cls_var, glyphs_first, glyphs_rest)],
            )
        )

    return result


__map = {
    "<": "sharp_start",
    ">": "sharp_end",
    "(": "circle_start",
    ")": "circle_end",
    "[": "block_start",
    "]": "block_end",
}


def tag_custom(content: str | Sequence[str | ast.Clazz], target: str):
    """
    Generate custom tag lookup.
    Args:
        content: The source glyphs to be replaced. Can be either a string or
            a sequence of strings/ast.Clazz objects.
        target: The target pattern to replace with. Must end with characters present
            in the ["<", ">", "(", ")", "[", "]"]. Middle characters must be ASCII letters.
    Returns:
        ast.Lookup: A Lookup object containing the substitution rules, named with pattern
            "custom_tag_{target middle chars}".
    Example:
        >>> tag_custom("_TODO_", "(TODO)")
    """
    glyphs = list(content)
    glyphs_len = len(glyphs)
    target_len = len(target)

    if target_len != glyphs_len:
        raise ValueError(
            f"length of `content` ({glyphs_len}) must be equal to length of `target` ({target_len})."
        )
    if target[-1] not in __map:
        raise ValueError(
            f"Last letter of `target` must in {list(__map.keys())}, current is '{target[-1]}'"
        )

    # Parse source
    source_list = []
    for g in glyphs:
        if isinstance(g, ast.Clazz):
            source_list.append(g)
        elif g.isalpha():
            source_list.append(f"@{g.upper()}")
        else:
            source_list.append(ast.gly(g))

    # Parse target
    target_list = []
    for target_gly in target:
        if target_gly in __map:
            target_list.append(f"{__map[target_gly]}.bg")
        elif target_gly.isalpha():
            target_list.append(f"{target_gly.upper()}.bg")
        else:
            raise Exception(
                f"All badge content must be in ASCII letters or {list(__map.keys())}, current is {target[1:-1]}"
            )

    # Generate substitutions in reverse order (from last glyph to first)
    result = []
    for i in range(glyphs_len, 0, -1):
        before = target_list[: i - 1]
        glyph = source_list[i - 1]
        after = source_list[i:] if i < glyphs_len else None
        replace = target_list[i - 1]
        result.append(ast.subst(before, glyph, after, replace))

    return ast.Lookup(name=f"custom_tag_{target[1:-1]}", desc=target, content=result)


upper_tag_text = [
    "trace",
    "debug",
    "info",
    "warn",
    "error",
    "fatal",
    "todo",
    "fixme",
]


def get_lookup(cls_var: ast.Clazz):
    return [
        tag_upper(upper_tag_text),
        tag_any(["todo", "fixme"], cls_var),
        # Mark annotation in Xcode, example: `// TODO: code review`
        # ast.subst_liga(source="TODO:", target="badge_todo.liga", lookup_name="todo_colon")
    ]
