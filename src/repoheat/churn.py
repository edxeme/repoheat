"""Per-file churn aggregation over a parsed change history.

Churn = added + deleted lines, summed across every commit that touched a
file — the classic signal for "this code lives dangerously".

Date filtering is done here, in Python, with explicit semantics: a commit
is kept when ``commit.date.date() >= since``. git's own ``--since`` is
approxidate — its cutoff depends on the host timezone and it excludes
same-day commits, which makes cross-machine results silently different.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime

from repoheat.gitlog import Commit


@dataclass
class FileChurn:
    """Lifetime change volume for one file."""

    path: str
    commits: int
    added: int
    deleted: int
    total: int
    last_touched: datetime


def aggregate(commits: list[Commit], *, since: str | None = None) -> list[FileChurn]:
    """Aggregate *commits* into per-file churn, heaviest first.

    ``since`` (``YYYY-MM-DD``) keeps commits from that day onward — the
    day boundary is inclusive, independent of the host timezone.
    """
    cutoff: date | None = date.fromisoformat(since) if since else None

    table: dict[str, FileChurn] = {}
    for commit in commits:
        if cutoff is not None and commit.date.date() < cutoff:
            continue
        for change in commit.files:
            entry = table.get(change.path)
            if entry is None:
                entry = FileChurn(
                    path=change.path,
                    commits=0,
                    added=0,
                    deleted=0,
                    total=0,
                    last_touched=commit.date,
                )
                table[change.path] = entry
            entry.commits += 1
            entry.added += change.added
            entry.deleted += change.deleted
            entry.total = entry.added + entry.deleted
            if commit.date > entry.last_touched:
                entry.last_touched = commit.date

    return sorted(table.values(), key=lambda c: (-c.total, c.path))
