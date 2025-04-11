from collections.abc import Sequence
import re


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
        return Line(f"{self.use()} = {cls(self.glyphs)};")


class Lookup:
    __slots__ = ("name", "desc", "content")

    def __init__(self, name: str, desc: str | None, content: list) -> None:
        self.name = name
        self.desc = desc
        self.content = content

    def use(self) -> Line:
        return Line(f"lookup {self.name};")

    def state(self) -> list[Line]:
        arr = []

        if self.desc:
            arr.append(Line(f"# {self.desc}"))

        arr.append(Line(f"lookup {self.name} {{"))

        for c in flatten_to_lines(self.content):
            arr.append(c.indent())

        arr.append(Line(f"}} {self.name};"))
        return arr


class Feature:
    __slots__ = ("tag", "content")

    def __init__(self, tag: str, content: Clazz | Lookup | Line | list):
        self.tag = tag
        self.content = content

    def use(self) -> Line:
        return Line(f"feature {self.tag};")

    def get_name_lines(self) -> list[Line]:
        return []

    def state(self) -> list[Line]:
        target = []
        for c in self.get_name_lines() + flatten_to_lines(self.content):
            target.append(c.indent())

        return [
            Line(f"feature {self.tag} {{"),
            Line(""),
            *target,
            Line(""),
            Line(f"}} {self.tag};"),
        ]


REGEXP = r"\(.*\)"


class CharacterVariant(Feature):
    __slots__ = ("id", "tag", "desc", "content")

    def __init__(self, id: int, desc: str, content: Clazz | Lookup | Line | list):
        if id < 1 or id > 99:
            raise TypeError(
                f"id should > 0 and < 100 in Character Variants, current is {id}"
            )
        self.id = id
        self.desc = desc
        Feature.__init__(self, f"cv{id:02d}", content)

    def get_name_lines(self) -> list[Line]:
        _name = re.sub(REGEXP, "", self.desc.replace("`", "")).strip()
        return [
            Line("cvParameters {"),
            Line("FeatUILabelNameID {", 1),
            Line(f'name "{_name}";', 2),
            Line("};", 1),
            Line("};"),
            Line(""),
        ]

    def desc_item(self) -> str:
        return f"- {self.tag}: {self.desc}"


class StylisticSet(Feature):
    __slots__ = ("id", "tag", "desc", "content")

    def __init__(self, id: int, desc: str, content: Clazz | Lookup | Line | list):
        if id < 1 or id > 20:
            raise TypeError(
                f"id should > 0 and < 20 in Stylistic Sets, current is {id}"
            )

        self.id = id
        self.desc = desc
        Feature.__init__(self, f"ss{id:02d}", content)

    def get_name_lines(self) -> list[Line]:
        _name = re.sub(REGEXP, "", self.desc.replace("`", "")).strip()
        return [
            Line("featureNames {"),
            Line(f'name "{_name}";', 1),
            Line("};"),
            Line(""),
        ]

    def desc_item(self):
        return f"- {self.tag}: {self.desc}"


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

LATIN_PUNCTUATIONS = list(__PUNCTUATION_MAP.keys())


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
    if isinstance(g, str) and len(g) > 1 and g[0] in __PUNCTUATION_MAP:
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


def cls(glyphs: str | Clazz | Sequence[str | Clazz], *rest: str | Clazz) -> str:
    """
    Generate inline class.

    >>> cls(["a", "@", "++", cl])
    "[a at plus_plus.liga @cl]"
    >>> cls("b", "_", "--", cl)
    "[b underscore hyphen_hyphen.liga @cl]"
    """
    glyphs_list = list(recursive_iterate(glyphs)) + list(rest)
    return "[" + " ".join([__parse_glyph(g) for g in glyphs_list]) + "]"


def cls_states(*cls: Clazz) -> list[Line]:
    """
    Declare classes with prefix empty line.
    """
    return [Line("")] + flatten_to_lines(cls)


def create(content: list, indent=2) -> str:
    lines = []
    for line in flatten_to_lines(content):
        # Skip duplicate empty lines
        if not line.text and lines and not lines[-1].text:
            continue

        # Add spacing before features and lookups
        if lines and lines[-1].text and not lines[-1].text.startswith("#"):
            if (
                line.text.startswith("#")
                or (line.text.startswith("lookup") and not line.text.endswith(";"))
                or (line.text.startswith("feature ") and line.text.endswith("{"))
            ):
                lines.append(Line(""))

        lines.append(line)

    return "\n".join(f"{' ' * (indent * line.level)}{line.text}" for line in lines)


def langsys(script: str, lang: str) -> Line:
    return Line(f"languagesystem {script} {lang};")


def lang(lang: str) -> Line:
    return Line(f"language {lang};")


def script(script: str) -> Line:
    return Line(f"script {script};")


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
    surround: list[tuple[Sequence[str | Clazz] | None, Sequence[str | Clazz] | None]] = [],
    banner: list[Line] | None = None,
) -> Lookup:
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
        surround: List of (prefix, suffix) tuples specifying contexts for substitution.
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
        >>> subst_liga("!=", surround=[((["a","b"], "c")), (cls, ["a","c"])])
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
        surround = [([],[])]

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

    return Lookup(
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


def recursive_iterate(data):
    if isinstance(data, Sequence) and not isinstance(data, str):
        for item in data:
            yield from recursive_iterate(item)
    else:
        yield data


def flatten_to_lines(data: Line | Clazz | Lookup | Feature | list | tuple) -> list[Line]:
    result = []

    for item in recursive_iterate(data):
        if isinstance(item, list):
            result += flatten_to_lines(item)
        elif isinstance(item, Clazz):
            result.append(item.state())
        elif isinstance(item, Line):
            result.append(item)
        elif isinstance(item, (Lookup, Feature)):
            result.extend(item.state())
        else:
            raise TypeError(f"Invalid item to flatten: {item}")

    return result
