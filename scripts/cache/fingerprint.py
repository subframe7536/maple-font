from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import TYPE_CHECKING

from scripts.cache.digest import digest_file, digest_tree

if TYPE_CHECKING:
    from pathlib import Path


@dataclass(frozen=True, order=True)
class FingerprintEntry:
    kind: str
    name: str
    digest: str


@dataclass(frozen=True)
class Fingerprint:
    """Immutable, inspectable collection of inputs to one build stage."""

    entries: tuple[FingerprintEntry, ...] = ()

    def _add(self, kind: str, name: str, digest: str) -> Fingerprint:
        entry = FingerprintEntry(kind, name, digest)
        return Fingerprint(tuple(sorted((*self.entries, entry))))

    def add_file(self, name: str, path: Path) -> Fingerprint:
        return self._add("file", name, digest_file(path))

    def add_tree(self, name: str, path: Path) -> Fingerprint:
        return self._add("tree", name, digest_tree(path))

    def add_json(self, name: str, value: object) -> Fingerprint:
        payload = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
        return self._add("json", name, hashlib.sha256(payload).hexdigest())

    def add_value(
        self, name: str, value: str | int | float | bool | None
    ) -> Fingerprint:
        return self.add_json(name, value)

    def add_upstream(self, name: str, identity: str) -> Fingerprint:
        return self._add("upstream", name, identity)

    def digest(self) -> str:
        payload = [(entry.kind, entry.name, entry.digest) for entry in self.entries]
        return hashlib.sha256(
            json.dumps(payload, separators=(",", ":")).encode()
        ).hexdigest()
