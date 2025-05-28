from source.py.feature import ast


class Seq:
    def __init__(self, g: str | list[str]) -> None:
        self.sta = ast.gly_seq(g, "sta")
        self.mid = ast.gly_seq(g, "mid")
        self.end = ast.gly_seq(g, "end")


def main_rules(g: str, cls_start: ast.Clazz, symbols: list[str]):
    prefix = []

    for s in symbols:
        prefix.append(ast.gly_seq(s + g, "sta"))
        prefix.append(ast.gly_seq(s + g, "mid"))

    prefix_cls = ast.cls(prefix, cls_start)

    return [
        ast.subst(prefix_cls, g, ast.cls(symbols, g), ast.gly_seq(g, "mid")),
        ast.subst(prefix_cls, g, None, ast.gly_seq(g, "end")),
        *[
            [
                ast.subst(cls_start, s, g, ast.gly_seq(s + g, "mid")),
                ast.subst(cls_start, s, None, ast.gly_seq(s + g, "end")),
                ast.subst(None, s, g, ast.gly_seq(s + g, "sta")),
            ]
            for s in symbols
        ],
        # Must be end of rules
        ast.subst(None, g, ast.cls(symbols, g), ast.gly_seq(g, "sta")),
    ]


def lookup_equals():
    eq_start = ast.gly_seq("=", "sta")
    eq_middle = ast.gly_seq("=", "mid")
    cls_start = ast.Clazz("EqualStart", [eq_start, eq_middle])

    return (
        ast.Lookup(
            "infinity_equal",
            "====",
            [
                cls_start.state(),
                # Disable |||
                ast.ign("|", "|", ["|", "="]),
                ast.ign("|", "|", "="),
                ast.ign(cls_start, "|", ["|", "|"]),
                # Main rules
                *main_rules("=", cls_start, ["<", ">"]),
                # Disable >=<
                ast.subst(">", "=", ["<", ast.cls("=", "<")], ast.gly_seq(">=", "sta")),
                ast.ign(">", "=", "<"),
                # Disable =<
                ast.subst(None, "=", ["<", ast.cls("=", "<")], eq_start),
                # Disable =/
                ast.subst(None, "=", ["/", ast.cls("=", "/")], eq_middle),
            ],
        ),
    )


def ss12_subst():
    return [
        lookup_equals(),
    ]


ss12_name = "Infinite hyphens and equals (`----`, `====`)"
ss12_feat = ast.StylisticSet(
    id=12, desc=ss12_name, content=ss12_subst(), version="7.3", sample="===="
)
