"""Parsing verified against repositories built with real git commands."""

from repoheat.gitlog import collect_history


def test_collects_full_history_from_real_repo(make_repo):
    repo = make_repo()

    commits = collect_history(repo)

    assert len(commits) == 3
    assert [c.author for c in commits] == [
        "Ada Lovelace",
        "Linus Torvalds",
        "Ada Lovelace",
    ]  # newest first, as git log prints


def test_commit_files_match_real_diffs(make_repo):
    repo = make_repo()

    commits = collect_history(repo)

    newest = commits[0]
    assert [(f.path, f.added, f.deleted) for f in newest.files] == [
        ("docs/readme.md", 1, 0)
    ]

    middle = commits[1]
    assert [(f.path, f.added, f.deleted) for f in middle.files] == [
        ("src/core.py", 1, 0)
    ]

    oldest = commits[2]
    assert [(f.path, f.added, f.deleted) for f in oldest.files] == [
        ("src/core.py", 3, 0)
    ]


def test_dates_are_timezone_aware_datetimes(make_repo):
    from datetime import datetime

    repo = make_repo()
    commits = collect_history(repo)

    assert isinstance(commits[0].date, datetime)
    assert commits[0].date.isoformat().endswith("-05:00")


def test_non_repository_raises(tmp_path):
    import pytest

    from repoheat.gitlog import GitHistoryError

    with pytest.raises(GitHistoryError, match="not a git repository"):
        collect_history(tmp_path)  # tmp_path exists but has no .git
