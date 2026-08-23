from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Protocol

from scripts.utils.logging import logger

if TYPE_CHECKING:
    from scripts.font_ops.fonttools import TTFont

INSTANCE_WEIGHT_MAPPING: dict[str, int] = {
    "thin": 100,
    "extralight": 200,
    "light": 300,
    "regular": 400,
    "medium": 500,
    "semibold": 600,
    "bold": 700,
    "extrabold": 800,
}

RESERVED_NAME_IDS = {1, 2, 3, 4, 5, 6, 16, 17, 25}


@dataclass(frozen=True)
class FontNamingSpec:
    """Encapsulates font naming parameters for OpenType name table updates."""

    family_name: str
    style_name: str
    full_name: str
    postscript_name: str
    is_skip_subfamily: bool = False
    preferred_family_name: str | None = None
    preferred_style_name: str | None = None
    narrow: bool = False
    variable: bool = False


class _NerdFontConfig(Protocol):
    @property
    def version(self) -> str: ...


class FontNameConfig(Protocol):
    @property
    def version_str(self) -> str: ...

    @property
    def beta(self) -> str | None: ...

    @property
    def nerd_font(self) -> _NerdFontConfig: ...

    @property
    def freeze_config_str(self) -> str: ...


def set_font_name(font: TTFont, name: str, name_id: int, mac: bool | None = None):
    font["name"].setName(name, nameID=name_id, platformID=3, platEncID=1, langID=0x409)
    if mac:
        font["name"].setName(
            name, nameID=name_id, platformID=1, platEncID=0, langID=0x0
        )


def get_font_name(font: TTFont, name_id: int) -> str:
    return (
        font["name"]
        .getName(nameID=name_id, platformID=3, platEncID=1, langID=0x409)
        .__str__()
    )


def del_font_name(font: TTFont, name_id: int):
    font["name"].removeNames(nameID=name_id)


def parse_style_name(style_name_compact: str):
    is_italic = style_name_compact.endswith("Italic")

    style_name = style_name_compact
    if is_italic and style_name_compact[0] != "I":
        style_name = style_name_compact[:-6] + " Italic"

    base_subfamily_list = ["Regular", "Bold", "Italic", "BoldItalic"]
    if style_name_compact in base_subfamily_list:
        return "", style_name, style_name, True, is_italic
    return (
        " " + style_name_compact.replace("Italic", ""),
        "Italic" if is_italic else "Regular",
        style_name,
        False,
        is_italic,
    )


def update_font_names(
    font: TTFont,
    font_config: FontNameConfig,
    spec: FontNamingSpec | None = None,
    *,
    family_name: str | None = None,
    style_name: str | None = None,
    full_name: str | None = None,
    postscript_name: str | None = None,
    is_skip_subfamily: bool = False,
    preferred_family_name: str | None = None,
    preferred_style_name: str | None = None,
    narrow: bool = False,
    variable: bool = False,
):
    if spec is None:
        if (
            family_name is None
            or style_name is None
            or full_name is None
            or postscript_name is None
        ):
            raise ValueError(
                "Either spec (FontNamingSpec) or required name fields must be provided"
            )
        spec = FontNamingSpec(
            family_name=family_name,
            style_name=style_name,
            full_name=full_name,
            postscript_name=postscript_name,
            is_skip_subfamily=is_skip_subfamily,
            preferred_family_name=preferred_family_name,
            preferred_style_name=preferred_style_name,
            narrow=narrow,
            variable=variable,
        )

    if spec.variable:
        ensure_variable_instance_names(
            font,
            postscript_prefix=spec.postscript_name.removesuffix(f"-{spec.style_name}"),
            italic=spec.style_name.endswith("Italic"),
        )
    font["name"].removeNames(platformID=1)
    if len(spec.family_name) > 31:
        logger.warning(
            "Family name may exceed legacy Windows limits: family=%s, length=%s",
            spec.family_name,
            len(spec.family_name),
        )
    set_font_name(font, spec.family_name, 1)
    set_font_name(font, spec.style_name, 2)
    suffix = ""
    if spec.variable:
        suffix += "Variable;"
    if "NF" in spec.postscript_name:
        suffix += f"NF{font_config.nerd_font.version};"
    if "CN" in spec.postscript_name and spec.narrow:
        suffix += "Narrow;"

    suffix += font_config.freeze_config_str
    beta_str = f"-{font_config.beta}" if font_config.beta else ""
    unique_identifier = (
        f"{font_config.version_str}{beta_str};SUBF;{spec.postscript_name};"
        f"2026;FL830;{suffix}"
    )

    set_font_name(font, unique_identifier, 3)
    set_font_name(font, spec.full_name, 4)
    set_font_name(font, font_config.version_str, 5)
    set_font_name(font, spec.postscript_name, 6)

    if spec.variable:
        set_font_name(font, spec.preferred_family_name or spec.family_name, 16)
        set_font_name(font, spec.preferred_style_name or spec.style_name, 17)
    elif (
        not spec.is_skip_subfamily
        and spec.preferred_family_name
        and spec.preferred_style_name
    ):
        set_font_name(font, spec.preferred_family_name, 16)
        set_font_name(font, spec.preferred_style_name, 17)
    elif spec.is_skip_subfamily:
        del_font_name(font, 16)
        del_font_name(font, 17)


def ensure_variable_instance_names(
    font: TTFont,
    postscript_prefix: str | None = None,
    italic: bool = False,
) -> None:
    """Give each fvar instance unique subfamily and PostScript name records."""
    if "fvar" not in font or "name" not in font:
        return

    name_table = font["name"]
    weight_names = {
        value: name.title().replace("Semibold", "SemiBold")
        for name, value in INSTANCE_WEIGHT_MAPPING.items()
    }
    used_name_ids = {record.nameID for record in name_table.names}
    next_name_id = max(used_name_ids, default=255) + 1
    instance_names: set[str] = set()

    for instance_index, instance in enumerate(font["fvar"].instances, start=1):
        weight = round(float(instance.coordinates.get("wght", 400)))
        fallback_name = weight_names.get(weight, str(weight))
        if italic:
            fallback_name = (
                "Italic" if fallback_name == "Regular" else f"{fallback_name}Italic"
            )
        current_name = name_table.getDebugName(instance.subfamilyNameID)
        name = (
            current_name
            if current_name and current_name not in {"Regular", "Italic"}
            else fallback_name
        )
        if name in instance_names:
            name = f"{name}-{weight}"
            if name in instance_names:
                name = f"{name}-{instance_index}"
        instance_names.add(name)

        name_id = _find_variable_instance_name_id(name_table, name)
        if name_id is None or name_id in RESERVED_NAME_IDS:
            while next_name_id in used_name_ids:
                next_name_id += 1
            name_id = next_name_id
            used_name_ids.add(name_id)
            next_name_id += 1
            set_font_name(font, name, name_id)
        instance.subfamilyNameID = name_id

        postscript_name = f"{postscript_prefix}-{name}" if postscript_prefix else name
        postscript_name_id = _find_variable_instance_name_id(
            name_table, postscript_name
        )
        if postscript_name_id is None or postscript_name_id in RESERVED_NAME_IDS:
            while next_name_id in used_name_ids:
                next_name_id += 1
            postscript_name_id = next_name_id
            used_name_ids.add(postscript_name_id)
            next_name_id += 1
            set_font_name(font, postscript_name, postscript_name_id)
        instance.postscriptNameID = postscript_name_id


def _find_variable_instance_name_id(name_table, value: str) -> int | None:
    for record in name_table.names:
        if record.nameID in RESERVED_NAME_IDS:
            continue
        try:
            if record.toUnicode() == value:
                return int(record.nameID)
        except UnicodeDecodeError:
            continue
    return None
