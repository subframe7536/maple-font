from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Literal

from scripts.cjk.config import config_from_json

if TYPE_CHECKING:
    from scripts.cjk.config import CJKBuildConfig

CJKPresetId = Literal["cn", "jp", "tc", "kr"]
DEFAULT_PRESET_ROOT = Path("sources/cjk")


@dataclass(frozen=True)
class CJKPresetSpec:
    preset_id: CJKPresetId
    label: str
    config_path: Path
    meta_languages: str
    code_page_range1: int


_PRESETS: dict[CJKPresetId, CJKPresetSpec] = {
    "cn": CJKPresetSpec(
        "cn",
        "Simplified Chinese",
        DEFAULT_PRESET_ROOT / "cn" / "config-cn.json",
        "Latn, Hans",
        1 << 0 | 1 << 18,
    ),
    "jp": CJKPresetSpec(
        "jp",
        "Japanese",
        DEFAULT_PRESET_ROOT / "jp" / "config-jp.json",
        "Latn, Jpan",
        1 << 0 | 1 << 17,
    ),
    "tc": CJKPresetSpec(
        "tc",
        "Traditional Chinese",
        DEFAULT_PRESET_ROOT / "tc" / "config-tc.json",
        "Latn, Hant",
        1 << 0 | 1 << 20,
    ),
    "kr": CJKPresetSpec(
        "kr",
        "Korean",
        DEFAULT_PRESET_ROOT / "kr" / "config-kr.json",
        "Latn, Hang",
        1 << 0 | 1 << 19,
    ),
}


def list_presets() -> tuple[CJKPresetId, ...]:
    return tuple(_PRESETS.keys())


def get_preset(preset_id: CJKPresetId) -> CJKPresetSpec:
    return _PRESETS[preset_id]


def build_preset_config(
    preset_id: CJKPresetId, root: str | None = None
) -> CJKBuildConfig:
    preset = get_preset(preset_id)
    config_path = (
        Path(root) / preset.config_path.relative_to(DEFAULT_PRESET_ROOT)
        if root
        else preset.config_path
    )
    return config_from_json(config_path)
