from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Any, Literal

if TYPE_CHECKING:
    from collections.abc import Iterable, Mapping

NerdFontSuffix = Literal["Mono", "Propo", ""]


@dataclass(frozen=True)
class NerdFontVariant:
    """Resolve shared Nerd Font suffix, symbol, and file naming rules."""

    suffix: NerdFontSuffix = ""

    @classmethod
    def from_options(
        cls,
        mono: bool = False,
        propo: bool = False,
        extra_args: Iterable[str] = (),
        *,
        reject_conflict: bool = False,
    ) -> NerdFontVariant:
        args = set(extra_args)
        if reject_conflict and mono and propo:
            raise ValueError(
                "Cannot build both `mono` and `propo` glyphs versions simultaneously."
            )
        if propo or "--variable-width-glyphs" in args:
            return cls("Propo")
        if mono or {"-s", "--mono", "--single-width-glyphs"} & args:
            return cls("Mono")
        return cls()

    @property
    def compact(self) -> str:
        return self.suffix[0] if self.suffix else ""

    @property
    def symbol(self) -> str:
        return f"NF{self.compact}"

    @property
    def directory_name(self) -> str:
        """Return the stable output and archive directory label."""
        return f"NF{self.suffix}"

    def cjk_directory_name(self, locale: str) -> str:
        return f"{self.directory_name}-{locale}"

    def base_path(self, source_dir: str | Path) -> Path:
        suffix = f"-{self.suffix}" if self.suffix else ""
        return Path(source_dir) / f"MapleMono-NF-Base{suffix}.ttf"

    def patched_style_path(
        self,
        output_dir: str | Path,
        family_name_compact: str,
        style: str = "Regular",
    ) -> Path:
        return Path(output_dir) / f"{family_name_compact}-{self.symbol}-{style}.ttf"

    def patched_font_path(self, output_dir: str | Path, font_basename: str) -> Path:
        return Path(output_dir) / font_basename.replace("-", f"NerdFont{self.suffix}-")


def parse_codes_from_json(
    path: str | Path = Path("FontPatcher") / "glyphnames.json",
) -> list[int]:
    """Return the Nerd Font codepoints declared in glyphnames.json."""
    data: Mapping[str, Any] = json.loads(Path(path).read_text(encoding="utf-8"))
    return sorted(
        {
            int(value["code"], 16)
            for value in data.values()
            if isinstance(value, dict) and "code" in value
        }
    )


__all__ = ["NerdFontVariant", "parse_codes_from_json"]
