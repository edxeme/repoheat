"""Shared fixtures: real git repositories built with real git commands.

Unit tests cover parsing with inline samples; these fixtures add repos
built with actual ``git init``/``add``/``commit`` calls, deterministic
authors and dates, so parsing is verified against git's *real* output
shapes end to end.
"""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

import pytest


def _git(repo: Path, *args: str, date: str | None = None, author: str | None = None):
    env = os.environ.copy()
    if date is not None:
        env["GIT_AUTHOR_DATE"] = date
        env["GIT_COMMITTER_DATE"] = date
    if author is not None:
        slug = author.lower().replace(" ", ".")
        env["GIT_AUTHOR_NAME"] = author
        env["GIT_AUTHOR_EMAIL"] = f"{slug}@example.com"
        env["GIT_COMMITTER_NAME"] = author
        env["GIT_COMMITTER_EMAIL"] = f"{slug}@example.com"
    subprocess.run(
        ["git", "-C", str(repo), *args], check=True, capture_output=True, env=env
    )


@pytest.fixture
def make_repo_with_renames(tmp_path: Path):
    """A repository with a binary file and a directory move (rename)."""
    def build() -> Path:
        repo = tmp_path / "renames"
        repo.mkdir()
        _git(repo, "init", "-q", "-b", "main")
        _git(repo, "config", "user.name", "Fallback User")
        _git(repo, "config", "user.email", "fallback@example.com")

        (repo / "notes.md").write_text("# notes\n")
        (repo / "logo.bin").write_bytes(b"\x00\x01\x02\x03")
        _git(repo, "add", "-A")
        _git(
            repo, "commit", "-q", "-m", "initial",
            date="2026-09-05T09:00:00-05:00", author="Ada Lovelace",
        )

        (repo / "docs").mkdir()
        _git(repo, "mv", "notes.md", "docs/notes.md")
        (repo / "docs" / "notes.md").write_text("# notes\n\nmore\n")
        _git(repo, "add", "-A")
        _git(
            repo, "commit", "-q", "-m", "move notes into docs",
            date="2026-09-06T10:00:00-05:00", author="Linus Torvalds",
        )
        return repo

    return build


@pytest.fixture
def make_repo(tmp_path: Path):
    """Build a small, deterministic repository and return its path.

    History: two authors, three commits — core.py created and extended,
    then a docs file added.
    """
    def build() -> Path:
        repo = tmp_path / "repo"
        repo.mkdir()
        _git(repo, "init", "-q", "-b", "main")
        _git(repo, "config", "user.name", "Fallback User")
        _git(repo, "config", "user.email", "fallback@example.com")

        (repo / "src").mkdir()
        (repo / "src" / "core.py").write_text("a = 1\nb = 2\nc = 3\n")
        _git(repo, "add", "-A")
        _git(
            repo, "commit", "-q", "-m", "add core",
            date="2026-09-01T09:00:00-05:00", author="Ada Lovelace",
        )

        (repo / "src" / "core.py").write_text("a = 1\nb = 2\nc = 3\nd = 4\n")
        _git(repo, "add", "-A")
        _git(
            repo, "commit", "-q", "-m", "extend core",
            date="2026-09-02T10:00:00-05:00", author="Linus Torvalds",
        )

        (repo / "docs").mkdir()
        (repo / "docs" / "readme.md").write_text("# repo\n")
        (repo / "src" / "core.py").write_text(
            "a = 1\nb = 2\nc = 3\nd = 4\n# reviewed\n"
        )
        _git(repo, "add", "-A")
        _git(
            repo, "commit", "-q", "-m", "add docs, review core",
            date="2026-09-03T11:30:00-05:00", author="Ada Lovelace",
        )
        return repo

    return build
