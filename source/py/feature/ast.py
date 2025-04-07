from collections.abc import Sequence


class Line:
    __slots__ = ("text", "level")

    def __init__(self, text: str, level=0) -> None:
        self.text = text
        self.level = level

    def indent(self) -> "Line":
        return Line(self.text, self.level + 1 if self.text else 0)


class Clazz:
    __slots__ = ("name", "glyphs")

    def __init__(self, name: str, glyphs: "Sequence[str | Clazz]" = []) -> None:
        self.name = name
        self.glyphs = tuple(glyphs)

    def use(self) -> str:
        return f"@{self.name}"

    def state(self) -> Line:
        return Line(f"{self.use()} = {clazz(self.glyphs)};")


__PUNCTUATION_MAP = {
    "{": "braceleft",
    "}": "braceright",
    "[": "bracketleft",
    "]": "bracketright",
    "(": "parenleft",
    ")": "parenright",
    "<": "less",
    ">": "greater",
    ".": "period",
    ",": "comma",
    "-": "hyphen",
    "_": "underscore",
    "=": "equal",
    "+": "plus",
    ":": "colon",
    ";": "semicolon",
    "?": "question",
    "!": "exclam",
    "@": "at",
    "#": "numbersign",
    "$": "dollar",
    "%": "percent",
    "^": "asciicircum",
    "&": "ampersand",
    "*": "asterisk",
    "'": "quotesingle",
    '"': "quotedbl",
    "/": "slash",
    "\\": "backslash",
    "|": "bar",
    "`": "grave",
    "~": "asciitilde",
}

__PUNCTUATION_CN_MAP = {
    "“": "quotedblleft",
    "”": "quotedblright",
    "‘": "quoteleft",
    "’": "quoteright",
    "…": "ellipsis",
    "—": "emdash",
}

LATIN_PUNCTUATIONS = set(__PUNCTUATION_MAP.keys())


def __gly(g: str | Clazz | Sequence[str | Clazz] | None) -> str:
    if not g:
        return ""
    if isinstance(g, list):
        return " ".join([__gly(_) for _ in g])
    if isinstance(g, Clazz):
        return g.use()
    if not isinstance(g, str):
        raise TypeError(f"{g}({type(g)}) is invalid for __gly")
    if g in __PUNCTUATION_MAP:
        return __PUNCTUATION_MAP[g]
    if g in __PUNCTUATION_CN_MAP:
        return __PUNCTUATION_CN_MAP[g]
    return g


def __prefix(data: str | Clazz | Sequence[str | Clazz] | None) -> str:
    if data:
        return __gly(data) + " "
    return ""


def __suffix(data: str | Clazz | Sequence[str | Clazz] | None) -> str:
    if data:
        return " " + __gly(data)
    return ""


def __subst(source: str, target: str) -> Line:
    return Line(f"sub {source} by {target};")


def __parse_glyph(g: str | Clazz):
    if isinstance(g, str) and len(g) > 1 and g[0] in LATIN_PUNCTUATIONS:
        return "_".join(map(__gly, list(g))) + ".liga"
    else:
        return __gly(g)


SPC = "SPC"


def gly(g: str | Clazz | Sequence[str | Clazz], suffix: str = "", overwrite=False):
    """
    Normalize glyph name.

    If no suffix and ``len(g) > 1``, suffix is ``".liga"``;
    else suffix is ``""``

    >>> gly("_")
    "underline"
    >>> gly("++")
    "plus_plus.liga"
    >>> gly("cl")
    "c_l.liga"
    >>> gly("--", ".suffix")
    "hyphen_hyphen.liga.suffix"
    >>> gly("--", ".suffix", True)
    "hyphen_hyphen.suffix"
    """
    if not isinstance(g, Clazz) and len(g) > 1:
        suf = suffix if overwrite else (".liga" + suffix)
        return "_".join(map(__gly, list(g))) + suf
    return __gly(g) + suffix


def clazz(glyphs: Sequence[str | Clazz]) -> str:
    """
    Generate inline class.

    >>> clazz(["a", "@", "++", cls])
    "[a at plus_plus.liga @cls]"
    """

    arr = []

    for g in glyphs:
        arr.append(__parse_glyph(g))

    return "[" + " ".join(arr) + "]"


def clazz_states(cls: Clazz | list[Clazz]) -> list[Line]:
    """
    Declare classes with prefix empty line.
    """
    return [Line("")] + flatten(cls)


def create(content: list, indent=2) -> str:
    _idt = indent * " "
    lines: list[Line] = []

    for line in flatten(content):
        if (
            len(lines) > 0
            and lines[-1].text
            and not lines[-1].text.startswith("#")
            and (
                line.text.startswith("#")
                or (line.text.startswith("lookup") and not line.text.endswith(";"))
            )
        ) or (line.text.startswith("feature ") and line.text.endswith("{")):
            lines.append(Line(""))
        lines.append(line)

    return "".join([("\n" + _idt * c.level + c.text) for c in lines])[1:]


def feature(tag: str, content: list) -> list[Line]:
    """Generate a feature block with indented content.
    This function creates a feature block with the specified tag and content,
    formatting it according to the OpenType feature file syntax.

    >>> feature("liga", [subst("a", "b", "c", "d")])
    [
        Line("feature liga {"),
        Line("sub a b' c by d"),
        Line("} liga;")
    ]
    """
    target = []
    for c in flatten(content):
        target.append(c.indent())

    return [Line(f"feature {tag} {{"), Line(""), *target, Line(""), Line(f"}} {tag};")]


def use_feature(name: str) -> Line:
    return Line(f"feature {name};")


def cv(id: int, name: str, content: list) -> list[Line]:
    """
    Generate Character Variants (cv) OpenType feature.
    Raises:
        TypeError: If id is not between 1 and 99.
    Example:
        >>> cv(1, "Alternate a", [Line("sub a by a.alt;")])
        [
            Line("feature cv01 {"),
            Line("cvParameters {"),
            Line("FeatUILabelNameID {", 1),
            Line('name "Alternate a";', 2),
            Line("};", 1),
            Line("sub a by a.alt"),
            Line("};"),
        ]
    """
    if id < 1 or id > 99:
        raise TypeError(
            f"id should > 0 and < 100 in Character Variants, current is {id}"
        )

    lines = [
        Line("cvParameters {"),
        Line("FeatUILabelNameID {", 1),
        Line(f'name "{name}";', 2),
        Line("};", 1),
        Line("};"),
    ]

    _content = flatten(content)

    if _content[0].text:
        lines.append(Line(""))

    lines += _content

    return feature(f"cv{id:02d}", lines)


def ss(id: int, name: str, content: list) -> list[Line]:
    """
    Creates stylistic set (ss) OpenType feature.
    Raises:
        TypeError: If the ID is not between 1 and 20
    Example:
        >>> ss(1, "Stylistic Set 1", [Line("sub a by a.ss01;")])
        [
            Line("feature ss01 {"),
            Line("featureNames {", 1),
            Line('name "Stylistic Set 1";', 2),
            Line("};", 1),
            Line("sub a by a.ss01;", 1),
            Line("};")
        ]
    """
    if id < 1 or id > 20:
        raise TypeError(f"id should > 0 and < 21 in Stylistic Sets, current is {id}")

    _content = flatten(content)
    lines = [
        Line("featureNames {"),
        Line(f'name "{name}";', 1),
        Line("};"),
    ]
    if _content[0].text:
        lines.append(Line(""))

    lines += _content

    return feature(f"ss{id:02d}", lines)


def langsys(script: str, lang: str) -> Line:
    return Line(f"languagesystem {script} {lang};")


def lang(lang: str) -> Line:
    return Line(f"language {lang};")


def script(script: str) -> Line:
    return Line(f"script {script};")


def lookup(name: str, desc: str | None, content: list) -> list[Line]:
    """
    Generate lookup table.

    >>> lookup("example", "Replace a with b", [Line("sub a by b;")])
    [
        Line("# Replace a with b"),
        Line("lookup example {"),
        Line("sub a by b;"),
        Line("} example;")
    ]
    """
    arr = []

    if desc:
        arr.append(Line(f"# {desc}"))

    arr.append(Line(f"lookup {name} {{"))

    for c in flatten(content):
        arr.append(c.indent())

    arr.append(Line(f"}} {name};"))
    return arr


def use_lookup(name: str) -> Line:
    return Line(f"lookup {name};")


def subst(
    prefix: str | Clazz | Sequence[str | Clazz] | None,
    glyph: str | Clazz,
    suffix: str | Clazz | Sequence[str | Clazz] | None,
    replace: str | Clazz,
) -> Line:
    """
    Generate substitution line.

    >>> subst(["-"], "b", cls, "d")
    Line("sub hyphen b' @cls by d;")
    """
    marker = "'"
    if not prefix and not suffix:
        marker = ""
    return __subst(
        f"{__prefix(prefix)}{__gly(glyph)}{marker}{__suffix(suffix)}",
        f"{__gly(replace)}",
    )


def subst_map(
    glyphs: str | list[str],
    source_suffix: str = "",
    target_suffix: str = "",
) -> list[Line]:
    """
    Generate substitution lines for a list of glyphs with a specified suffix.

    >>> subst_map(["Q", "all", "{{"], target_suffix=".cv01")
    [
        Line("sub Q by Q.cv01;"),
        Line("sub all by all.cv01;"),
        Line("sub braceleft_braceleft.liga by braceleft_braceleft.liga.cv01;")
    ]
    """
    result = []

    if isinstance(glyphs, str):
        glyphs = [glyphs]

    for g in glyphs:
        _g = __parse_glyph(g)
        result.append(__subst(f"{_g}{source_suffix}", f"{_g}{target_suffix}"))

    return result


def subst_liga(
    source: str | list[str],
    target: str | None = None,
    lookup_name: str | None = None,
    desc: str | None = None,
    surround: list[list[Sequence[str | Clazz]]] = [],
    banner: list[Line] | None = None,
):
    """
    Generate substitution lines for target ligature.

    Default ``target`` is ``gly(source)``

    Default ``lookup_name`` is ``target``

    Args:
        source: The glyphs to form the ligature (e.g., "!=" or ["!", "="]).
        target: The ligature glyph name; defaults to ``gly(source)``.
        lookup_name: Name of the lookup block; defaults to ``target``.
        desc: Content of comment before the lookup block; defaults to ``source``,
            or ``lookup_name`` if ``source`` is ``list``.
        surround: List of [prefix, suffix] pairs specifying contexts for substitution.
            Each prefix/suffix is ``Sequence[str | Clazz]``.
            If empty, generates basic substitution rules without context.
        banner: List of substitution rules before the main rules in lookup block.

    Returns:
        list[Line]: Lines forming a lookup block with substitution rules.

    Examples:
        >>> subst_liga("!=", banner=[ignore("a", "b", "c")])
        [
            Line("lookup exclam_equal.liga {"),
            Line("ignore sub a b' c;"),
            Line("sub exclam' equal by SPC;"),
            Line("sub SPC equal' by exclam_equal.liga;"),
            Line("} lookup exclam_equal.liga;")
        ]
        >>> subst_liga("!=", surround=[[["a","b"], "c"], [cls, ["a","c"]]])
        [
            Line("lookup exclam_equal.liga {"),
            Line("sub a b exclam' equal c by SPC;"),
            Line("sub @cls exclam' equal a c by SPC;"),
            Line("sub a b SPC equal' c by exclam_equal.liga;"),
            Line("sub @cls SPC equal' a c by exclam_equal.liga;"),
            Line("} lookup exclam_equal.liga;")
        ]
    """
    source_arr = list(source)
    if not target:
        target = gly(source)
    if not lookup_name:
        lookup_name = target
    if not desc:
        desc = source if isinstance(source, str) else lookup_name
    if banner is None:
        banner = []

    def to_list(item):
        if item is None:
            return []
        elif isinstance(item, (str, Clazz)):
            return [item]
        else:
            return list(item)

    subst_rules = []
    if not surround:
        surround = [[[], []]]

    for prfx, sfx in surround:
        prfx_list = to_list(prfx)
        sfx_list = to_list(sfx)
        n = len(source_arr)

        for i in range(n - 1):
            subst_prefix = prfx_list + [SPC] * i
            subst_suffix = source_arr[i + 1 :] + sfx_list
            subst_rules.insert(0, subst(subst_prefix, source_arr[i], subst_suffix, SPC))

        subst_prefix = prfx_list + [SPC] * (n - 1)
        subst_rules.insert(0, subst(subst_prefix, source_arr[-1], sfx_list, target))

    return lookup(
        lookup_name,
        desc,
        banner + subst_rules,
    )


def ignore(
    prefix: str | Clazz | Sequence[str | Clazz] | None,
    glyph: str,
    suffix: str | Clazz | Sequence[str | Clazz] | None,
) -> Line:
    """
    Generate ignore rule.

    >>> ignore("{", "b", ["c", "d"])
    Line("ignore sub braceleft b' c d;")
    >>> ignore(["_", "_"], "b", cls)
    Line("ignore sub underscore underscore b' @cls;")
    """
    return Line(f"ignore sub {__prefix(prefix)}{__gly(glyph)}'{__suffix(suffix)};")


def flatten(data: Line | Clazz | list) -> list[Line]:
    if isinstance(data, Clazz):
        return [data.state()]
    elif isinstance(data, Line):
        return [data]

    result = []
    for item in data:
        if isinstance(item, list):
            result += flatten(item)
        elif isinstance(item, Clazz):
            result.append(item.state())
        elif isinstance(item, Line):
            result.append(item)
        else:
            raise TypeError(f"Invalid item: {item} ({type(item)})")
    return result
