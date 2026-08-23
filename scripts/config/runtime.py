from __future__ import annotations

from dataclasses import asdict, dataclass
from os import listdir, path
from pathlib import Path
from typing import TYPE_CHECKING, Any

from scripts.external.process import get_font_forge_bin
from scripts.utils.downloads import github_host
from scripts.utils.files import join_path

if TYPE_CHECKING:
    from scripts.config.base import ResolvedConfig


def check_file_count(
    dir_path: str, min_count: int = 16, end: str | None = None
) -> bool:
    return path.isdir(dir_path) and (
        len([file for file in listdir(dir_path) if end is None or file.endswith(end)])
        >= min_count
    )


@dataclass(slots=True)
class BuildRuntimeContext:
    src_dir: str
    output_root: str
    output_otf: str
    output_ttf: str
    output_ttf_hinted: str
    output_variable: str
    output_woff2: str
    output_nf: str
    ttf_base_dir: str
    has_cache: bool
    is_nf_built: bool
    is_cjk_built: bool
    effective_github_mirror: str
    font_forge_bin: str | None
    resolved_vertical_metric: tuple[int, int]

    @classmethod
    def from_config(cls, config: ResolvedConfig) -> BuildRuntimeContext:
        output_root = "fonts"
        output_ttf = join_path(output_root, "TTF")
        output_ttf_hinted = join_path(output_root, "TTF-AutoHint")
        nf_variant = config.get_nf_variant()
        return cls(
            src_dir="sources",
            output_root=output_root,
            output_otf=join_path(output_root, "OTF"),
            output_ttf=output_ttf,
            output_ttf_hinted=output_ttf_hinted,
            output_variable=join_path(output_root, "Variable"),
            output_woff2=join_path(output_root, "Woff2"),
            output_nf=join_path(output_root, nf_variant.directory_name),
            ttf_base_dir=output_ttf_hinted if config.use_hinted else output_ttf,
            has_cache=(
                check_file_count(
                    join_path(output_root, "Variable"), min_count=2, end=".ttf"
                )
                and check_file_count(output_ttf, min_count=4, end=".ttf")
                and (
                    not config.needs_hinted_ttf()
                    or check_file_count(output_ttf_hinted, min_count=4, end=".ttf")
                )
                and (
                    not config.wants_format("otf")
                    or check_file_count(
                        join_path(output_root, "OTF"), min_count=4, end=".otf"
                    )
                )
                and (
                    not config.wants_format("woff2")
                    or check_file_count(
                        join_path(output_root, "Woff2"), min_count=4, end=".woff2"
                    )
                )
            ),
            is_nf_built=False,
            is_cjk_built=False,
            effective_github_mirror=github_host(config.github_mirror),
            font_forge_bin=get_font_forge_bin(),
            resolved_vertical_metric=config.vertical_metric,
        )

    @property
    def output_dir(self) -> str:
        return self.output_root

    @property
    def output_nf_variable(self) -> str:
        return join_path(self.output_root, f"Variable-{Path(self.output_nf).name}")

    def feature_file_path(self, is_italic: bool, is_cjk: bool = False) -> str:
        return join_path(
            self.src_dir,
            "features",
            ("italic" if is_italic else "regular") + ("_cn" if is_cjk else "") + ".fea",
        )

    def to_dict(self, config: ResolvedConfig | None = None) -> dict[str, Any]:
        data = asdict(self)
        data["output_nf_variable"] = self.output_nf_variable
        if config is not None:
            data["use_font_patcher"] = config.nerd_font.uses_font_patcher()
        return data
