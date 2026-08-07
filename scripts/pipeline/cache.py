from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Any

from scripts.cache.digest import digest_paths
from scripts.cache.fingerprint import Fingerprint
from scripts.utils.logging import logger

CACHE_SCHEMA = 3
CACHE_FILE_NAME = "build-cache.json"


def cache_record_path(output_root: str | Path) -> Path:
    return Path(output_root) / CACHE_FILE_NAME


def _digest(value: Any) -> str:
    return Fingerprint().add_json("value", value).digest()


def stage_identity(
    build_identity: dict[str, Any],
    stage: str,
    dependencies: dict[str, str] | None = None,
) -> str:
    """Return a stable key for one stage and its upstream keys."""
    fingerprint = (
        Fingerprint().add_value("stage", stage).add_json("inputs", build_identity)
    )
    for name, identity in sorted((dependencies or {}).items()):
        fingerprint = fingerprint.add_upstream(name, identity)
    return fingerprint.digest()


def relative_cache_path(root: Path, path: Path) -> str:
    return path.resolve().relative_to(root.resolve()).as_posix()


def stage_digest(root: Path, paths: list[Path]) -> str:
    """Hash one stage, including relative names and file contents."""
    return digest_paths(root, tuple(path for path in paths if path.is_file()))


def output_snapshot(
    root: Path,
    stage: str,
    paths: list[Path],
) -> dict[str, object]:
    """Create one stage digest and its exact relative output path list."""
    files = sorted(relative_cache_path(root, path) for path in paths if path.is_file())
    digest = stage_digest(root, [root / relative for relative in files])
    logger.debug(
        "Cache stage: stage=%s, files=%s, digest=%s", stage, len(files), digest
    )
    return {"files": files, "digest": digest}


def read_cache_record(root: Path) -> dict[str, Any] | None:
    path = cache_record_path(root)
    if not path.is_file():
        logger.info("Cache record: path=%s, status=missing", CACHE_FILE_NAME)
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        logger.info("Cache record: path=%s, status=invalid", CACHE_FILE_NAME)
        return None
    if (
        not isinstance(data, dict)
        or data.get("schema") != CACHE_SCHEMA
        or not isinstance(data.get("stages"), dict)
    ):
        logger.info("Cache record: path=%s, status=invalid", CACHE_FILE_NAME)
        return None
    logger.info("Cache record: path=%s, status=found", CACHE_FILE_NAME)
    return data


def write_cache_record(root: Path, record: dict[str, Any]) -> None:
    path = cache_record_path(root)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(
        json.dumps(record, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    temporary.replace(path)


def validate_stage(
    root: Path,
    record: dict[str, Any] | None,
    stage: str,
    identity: str,
    expected_paths: list[Path],
) -> bool:
    return (
        validated_stage_record(root, record, stage, identity, expected_paths)
        is not None
    )


def validated_stage_record(
    root: Path,
    record: dict[str, Any] | None,
    stage: str,
    identity: str,
    expected_paths: list[Path],
) -> dict[str, object] | None:
    """Validate a stage and return an independent copy of its original record."""
    stages = (record or {}).get("stages")
    stage_record = stages.get(stage) if isinstance(stages, dict) else None
    if not isinstance(stage_record, dict):
        logger.info("Cache miss: stage=%s, reason=missing-record", stage)
        return None
    if stage_record.get("key") != identity:
        logger.info("Cache miss: stage=%s, reason=identity-changed", stage)
        return None

    snapshot = stage_record.get("snapshot")
    if not isinstance(snapshot, dict):
        logger.info("Cache miss: stage=%s, reason=invalid-record", stage)
        return None
    files = snapshot.get("files")
    digest = snapshot.get("digest")
    if not isinstance(files, list) or not all(isinstance(item, str) for item in files):
        logger.info("Cache miss: stage=%s, reason=invalid-record", stage)
        return None
    expected = {relative_cache_path(root, path) for path in expected_paths}
    if expected != set(files):
        logger.info("Cache miss: stage=%s, reason=missing-output", stage)
        return None
    if any(not path.is_file() or path.stat().st_size == 0 for path in expected_paths):
        logger.info("Cache miss: stage=%s, reason=missing-output", stage)
        return None
    if not isinstance(digest, str) or digest != stage_digest(root, expected_paths):
        logger.info("Cache miss: stage=%s, reason=stage-digest-mismatch", stage)
        return None
    logger.info("Cache hit: stage=%s", stage)
    return deepcopy(stage_record)
