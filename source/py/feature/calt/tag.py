from source.py.feature import ast


def upper_badge(text: str):
    source = ["["] + [g.upper() for g in text] + ["]"]
    return ast.subst_liga(
        source,
        target=f"badge_{text}.liga",
        lookup_name=f"badge_{text}",
        desc="".join(source),
    )


def any_badge(text: str, cls_var: ast.Clazz):
    glyphs_first = f"@{text[0].upper()}"
    glyphs_rest = [f"@{g.upper()}" for g in text[1:]] + [")", ")"]
    return ast.subst_liga(
        [glyphs_first] + glyphs_rest,
        target=f"badge_{text}.liga",
        lookup_name=f"badge_{text}_alt",
        desc=f"{text}))",
        banner=[ast.ignore(cls_var, glyphs_first, glyphs_rest)],
    )


# def colon_badge(text: str):
#     return ast.subst_liga(
#         [g.upper() for g in text] + [":"],
#         target=f"badge_{text}.liga",
#         lookup_name=f"badge_{text}_colon",
#         desc=f" {text}:",
#     )


def get_lookup(cls_var: ast.Clazz):
    return [
        upper_badge("trace"),
        upper_badge("debug"),
        upper_badge("info"),
        upper_badge("warn"),
        upper_badge("error"),
        upper_badge("fatal"),
        upper_badge("todo"),
        upper_badge("fixme"),
        any_badge("todo", cls_var),
        any_badge("fixme", cls_var),
        # colon_badge("todo")
    ]
