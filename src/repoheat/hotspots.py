"""Change hotspots and knowledge concentration.

- **Hotspots** combine churn with current file size: a file that changes
  constantly *and* is large today is where defects and effort concentrate.
  Score = churn × size (Tornhill-style, with size as a cheap stand-in for
  complexity).
- **Bus factor** counts distinct authors per file: high churn with few
  authors means knowledge locked in one head.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from repoheat.churn import FileChurn, aggregate
from repoheat.gitlog import Commit


@dataclass
class Hotspot:
    """One file ranked by churn × current size."""

    path: str
    churn: int
    size: int
    score: int


@dataclass
class BusFactor:
    """One file's knowledge concentration."""

    path: str
    authors: int
    commits: int
    main_author: str


def _file_size(root: Path, rel_path: str) -> int:
    """Current line count of a file, or 0 when it no longer exists."""
    target = root / rel_path
    if not target.is_file():
        return 0
    try:
        return len(target.read_text(encoding="utf-8", errors="ignore").splitlines())
    except OSError:
        return 0


def hotspots(root: Path, history: list[Commit], *, top: int = 10) -> list[Hotspot]:
    """Rank files by churn × current size, heaviest first."""
    ranked: list[Hotspot] = []
    for entry in aggregate(history):
        size = _file_size(root, entry.path)
        ranked.append(
            Hotspot(path=entry.path, churn=entry.total, size=size, score=entry.total * size)
        )
    ranked.sort(key=lambda h: (-h.score, -h.churn, h.path))
    return ranked[:top]


def bus_factor(history: list[Commit], *, top: int = 10) -> list[BusFactor]:
    """Files by knowledge concentration: fewest authors, most commits first."""
    authors_by_file: dict[str, dict[str, int]] = {}
    for commit in history:
        for change in commit.files:
            counter = authors_by_file.setdefault(change.path, {})
            counter[commit.author] = counter.get(commit.author, 0) + 1

    rows = [
        BusFactor(
            path=path,
            authors=len(counter),
            commits=sum(counter.values()),
            main_author=max(counter, key=lambda name: counter[name]),
        )
        for path, counter in authors_by_file.items()
    ]
    rows.sort(key=lambda r: (r.authors, -r.commits, r.path))
    return rows[:top]
