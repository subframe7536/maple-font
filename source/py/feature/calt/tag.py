from source.py.feature import ast


def upper_tag(text: str):
    source = ["["] + [g.upper() for g in text] + ["]"]
    return ast.subst_liga(
        source,
        target=f"badge_{text}.liga",
        lookup_name=f"badge_{text}",
        desc="".join(source),
    )


def any_tag(text: str, cls_var: ast.Clazz):
    glyphs_first = f"@{text[0].upper()}"
    glyphs_rest = [f"@{g.upper()}" for g in text[1:]] + [")", ")"]
    return ast.subst_liga(
        [glyphs_first] + glyphs_rest,
        target=f"badge_{text}.liga",
        lookup_name=f"badge_{text}_alt",
        desc=f"{text}))",
        banner=[ast.ignore(cls_var, glyphs_first, glyphs_rest)],
    )


def get_lookup(cls_var: ast.Clazz):
    return [
        upper_tag("trace"),
        upper_tag("debug"),
        upper_tag("info"),
        upper_tag("warn"),
        upper_tag("error"),
        upper_tag("fatal"),
        upper_tag("todo"),
        upper_tag("fixme"),
        any_tag("todo", cls_var),
        any_tag("fixme", cls_var),
        # Support Mark annotation in Xcode, example: `// TODO: code review`
        # ast.subst_liga(source="TODO:", target="badge_todo.liga", lookup_name="todo_colon")
    ]
