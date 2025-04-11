from source.py.feature import ast


def upper_tag(text: str):
    source = ["["] + [g.upper() for g in text] + ["]"]
    return ast.subst_liga(
        source,
        target=f"badge_{text}.liga",
        lookup_name=f"badge_{text}",
        desc="".join(source)
    )


def any_tag(text: str):
    return ast.subst_liga(
        [f"@{g.upper()}" for g in text] + [")", ")"],
        target=f"badge_{text}.liga",
        lookup_name=f"badge_{text}_alt",
        desc=f"{text}))"
    )


def get_lookup():
    return [
        upper_tag("trace"),
        upper_tag("debug"),
        upper_tag("info"),
        upper_tag("warn"),
        upper_tag("error"),
        upper_tag("fatal"),
        upper_tag("todo"),
        upper_tag("fixme"),
        any_tag("todo"),
        any_tag("fixme"),
    ]
