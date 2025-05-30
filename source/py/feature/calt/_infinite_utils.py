import source.py.feature.ast as ast


__USE_INFINITE = True


def use_infinite():
    return __USE_INFINITE

def ignore_when_using_infinite(*items: ast.Lookup):
    if __USE_INFINITE:
        return None
    return items


def infinite_rules(
    g: str, cls_start: ast.Clazz, symbols: list[str], extra_rules: list[ast.Line] = []
):
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
        *extra_rules,
        # Must be end of rules
        ast.subst(None, g, ast.cls(symbols, g), ast.gly_seq(g, "sta")),
    ]
