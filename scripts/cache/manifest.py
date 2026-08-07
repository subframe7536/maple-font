from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from scripts.cache.fingerprint import Fingerprint


@dataclass(frozen=True)
class StageManifest:
    version: int
    stage: str
    fingerprint: Fingerprint
    output_digest: str
    outputs: tuple[str, ...]

    @property
    def identity(self) -> str:
        return self.fingerprint.digest()

    def as_dict(self) -> dict[str, object]:
        return asdict(self)
