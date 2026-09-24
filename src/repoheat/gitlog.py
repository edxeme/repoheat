"""Parse ``git log --numstat`` output into a structured change history.

The history of a repository *is* a large data source — real projects have
tens of thousands of commits. This module shells out to git once, parses
the stream with record/field separators (so author names and paths with
spaces or special characters survive intact), and hands out plain
dataclasses the rest of the tool works with.
"""

from __future__ import annotations

import subprocess
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Callable

_RECORD = "\x1e"  # ASCII record separator — one per commit
_FIELD = "\x1f"  # ASCII unit separator — between header fields

#: One git invocation yields the whole history: hashes, author dates,
#: author names (%aN — .mailmap-resolved), and per-file add/del counts.
LOG_FORMAT = f"--pretty=format:{_RECORD}%H{_FIELD}%ad{_FIELD}%aN"

#: ``-M`` so renames are detected and reported as renames, not add+delete.


@dataclass
class FileChange:
    """One file touched by one commit."""

    path: str
    added: int = 0
    deleted: int = 0
    binary: bool = False


@dataclass
class Commit:
    """One commit: identity, point in time, author and touched files."""

    sha: str
    date: datetime
    author: str
    files: list[FileChange] = field(default_factory=list)


class GitHistoryError(RuntimeError):
    """Raised when git history cannot be collected or parsed."""


def numstat_argv(path: Path) -> list[str]:
    """The exact git invocation used to collect history."""
    return [
        "git",
        "-C",
        str(path),
        "log",
        "--no-merges",
        "--no-color",
        "-M",
        "--date=iso-strict",
        LOG_FORMAT,
        "--numstat",
    ]


def collect_history(
    path: Path,
    *,
    runner: Callable[..., subprocess.CompletedProcess] = subprocess.run,
) -> list[Commit]:
    """Collect and parse the change history of the repository at *path*.

    Date filtering is deliberately NOT delegated to git: ``--since`` with a
    bare date is approxidate — its cutoff depends on the host timezone and
    it excludes same-day commits. Callers filter parsed commits in Python
    instead, where semantics are explicit.
    """
    try:
        proc = runner(numstat_argv(path), capture_output=True, text=True)
    except OSError as exc:
        raise GitHistoryError(f"git is not available: {exc}") from exc

    if proc.returncode != 0:
        raise GitHistoryError(proc.stderr.strip() or "git log failed")
    return parse_log_output(proc.stdout)


def parse_log_output(text: str) -> list[Commit]:
    """Parse the captured output of :func:`numstat_argv`."""
    commits: list[Commit] = []
    for record in text.split(_RECORD):
        record = record.strip()
        if not record:
            continue

        lines = record.split("\n")
        sha, date_raw, author = lines[0].split(_FIELD)
        commit = Commit(
            sha=sha,
            date=datetime.fromisoformat(date_raw),
            author=author,
        )
        for line in lines[1:]:
            if not line.strip():
                continue
            added_raw, deleted_raw, path = line.split("\t", 2)
            commit.files.append(
                FileChange(path=path, added=int(added_raw), deleted=int(deleted_raw))
            )
        commits.append(commit)
    return commits
