from source.py.feature import ast


def tag_upper(text_list: list[str]):
    result = []

    for text in text_list:
        source = ["["] + [g.upper() for g in text] + ["]"]
        result.append(
            ast.subst_liga(
                source,
                target=f"tag_{text}.liga",
                lookup_name=f"tag_{text}",
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
                target=f"tag_{text}.liga",
                lookup_name=f"tag_{text}_alt",
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


def tag_custom(
    content_list: list[tuple[str, str]],
    bg_cls: dict[str, ast.Clazz],
):
    """
    Generate custom tag lookup.

    ``content_list`` is `list[(content, target)]`
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
    result = []
    for source, target in content_list:
        glyphs = list(source)
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
            if g.isalpha():
                source_list.append(f"@{g.upper()}")
            else:
                source_list.append(ast.gly(g))

        # Parse target
        target_list = []
        for target_gly in target:
            if target_gly in __map:
                target_list.append(f"{__map[target_gly]}.bg")
            elif target_gly.isalpha():
                up = target_gly.upper()
                if up in bg_cls:
                    target_list.append(bg_cls[up])
                else:
                    target_list.append(f"{up}.bg")
            else:
                raise Exception(
                    f"All tag content must be in ASCII letters or {list(__map.keys())}, current is {target[1:-1]}"
                )

        # Generate substitutions in reverse order (from last glyph to first)
        subst_list = []
        for i in range(glyphs_len, 0, -1):
            before = target_list[: i - 1]
            glyph = source_list[i - 1]
            after = source_list[i:] if i < glyphs_len else None
            replace = target_list[i - 1]
            if isinstance(replace, ast.Clazz):
                replace = replace.glyphs[0]
            subst_list.append(ast.subst(before, glyph, after, replace))

        desc = []
        for item in source_list:
            if isinstance(item, str):
                desc.append(item.replace("@", ""))
            elif isinstance(item, ast.Clazz):
                desc.append(f"_{item.name}_")

        lookup_name = f"custom_tag_{"_".join(desc)}"

        result.append(
            ast.Lookup(
                name=lookup_name,
                desc=source,
                content=subst_list,
            )
        )

    return result


upper_tag_text = [
    "trace",
    "debug",
    "info",
    "warn",
    "error",
    "fatal",
    "todo",
    "fixme",
    "note",
    "hack",
    "mark",
    "eror",
    "warning",
]


def get_lookup(cls_var: ast.Clazz):
    bg_cls = {}
    for item in cls_var.glyphs:
        if not isinstance(item, ast.Clazz):
            continue

        first = item.glyphs[0]
        if not isinstance(first, str) or len(first) > 1 or not first.isalpha():
            continue

        gly_list = [f"{first}.bg"]
        for gly in item.glyphs[1:]:
            if isinstance(gly, str) and gly.startswith(first):
                _, feat = gly.split(".", 1)
                gly_list.append(f"{first}.bg.{feat}")

        if len(gly_list) > 1:
            bg_cls[first] = ast.Clazz(f"Bg{first.capitalize()}", gly_list)

    return [
        ast.cls_states(*bg_cls.values()),
        tag_upper(upper_tag_text),
        tag_any(["todo", "fixme"], cls_var),
        # =========================================================
        #                       Custom tags
        # ---------------------------------------------------------
        tag_custom(
            [
                # ("_bug_", "[bug]"),
                # ("_noqa_", "(noqa)"),
            ],
            bg_cls,
        ),
        # =========================================================
        #                Mark annotation in Xcode
        #             example: `// TODO: code review`
        # ---------------------------------------------------------
        # ast.subst_liga(
        #     source="TODO:",
        #     target="tag_todo.liga",
        #     lookup_name="todo_colon"
        # )
        # ast.subst_liga(
        #     source="MARK:",
        #     target="tag_todo.liga",
        #     lookup_name="mark_colon"
        # )
        # =========================================================
    ]
