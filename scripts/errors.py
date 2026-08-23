from __future__ import annotations

from dataclasses import dataclass


class BuildError(Exception):
    """Base class for actionable build-system failures."""


class BuildDependencyError(BuildError, RuntimeError):
    """Raised when a required local build dependency is unavailable."""


class CJKSourceUnavailable(BuildDependencyError):
    """Raised when an explicitly requested CJK source cannot be resolved."""


class CJKBaseUnavailable(BuildDependencyError):
    """Raised when no valid CJK base can be resolved."""


class DownloadError(BuildError, FileNotFoundError):
    """Raised when an external source cannot be downloaded."""


class ArchiveError(DownloadError, ValueError):
    """Raised when a downloaded archive is invalid or unsafe."""


class ArchiveMemberNotFoundError(ArchiveError):
    """Raised when the requested archive member is absent or ambiguous."""


@dataclass(frozen=True)
class ExternalToolError(BuildError):
    """A failed external command with complete, structured diagnostics."""

    command: tuple[str, ...]
    exit_code: int
    stdout: str
    stderr: str

    def __str__(self) -> str:
        argv = " ".join(repr(argument) for argument in self.command)
        details = [f"Command failed with exit code {self.exit_code}: {argv}"]
        if self.stdout:
            details.append(f"stdout:\n{self.stdout.rstrip()}")
        if self.stderr:
            details.append(f"stderr:\n{self.stderr.rstrip()}")
        return "\n".join(details)
