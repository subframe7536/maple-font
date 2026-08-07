from __future__ import annotations

import hashlib
import os
import stat
from pathlib import Path
from typing import BinaryIO

_CHUNK_SIZE = 1024 * 1024


def _field(hasher: object, name: bytes, value: bytes) -> None:
    """Hash a length-delimited field so adjacent values cannot collide."""
    digest = hasher
    digest.update(len(name).to_bytes(4, "big"))  # type: ignore[attr-defined]
    digest.update(name)  # type: ignore[attr-defined]
    digest.update(len(value).to_bytes(8, "big"))  # type: ignore[attr-defined]
    digest.update(value)  # type: ignore[attr-defined]


def _contents(hasher: object, source: BinaryIO) -> None:
    while chunk := source.read(_CHUNK_SIZE):
        _field(hasher, b"chunk", chunk)


def digest_paths(root: Path, paths: list[Path] | tuple[Path, ...]) -> str:
    """Hash paths canonically, including names, kinds, sizes, and contents."""
    root = Path(os.path.abspath(root))
    hasher = hashlib.sha256()
    normalized = sorted(
        {Path(os.path.abspath(path)) for path in paths}, key=lambda p: p.as_posix()
    )
    for path in normalized:
        relative = path.relative_to(root).as_posix().encode()
        mode = path.lstat().st_mode
        kind = (
            b"file"
            if stat.S_ISREG(mode)
            else b"symlink"
            if stat.S_ISLNK(mode)
            else b"other"
        )
        _field(hasher, b"entry", b"")
        _field(hasher, b"path", relative)
        _field(hasher, b"type", kind)
        if kind == b"file":
            size = path.stat().st_size
            _field(hasher, b"size", size.to_bytes(8, "big"))
            with path.open("rb") as source:
                _contents(hasher, source)
        elif kind == b"symlink":
            _field(hasher, b"target", path.readlink().as_posix().encode())
    return hasher.hexdigest()


def digest_file(path: Path) -> str:
    return digest_paths(path.parent, [path])


def digest_tree(root: Path) -> str:
    root = Path(os.path.abspath(root))
    paths = [path for path in root.rglob("*") if not path.is_dir()]
    return digest_paths(root, paths)
