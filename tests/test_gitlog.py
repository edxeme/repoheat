"""Parser tests against captured git log samples (inline fixtures)."""

from datetime import datetime
from pathlib import Path

import pytest

from repoheat.gitlog import GitHistoryError, collect_history, parse_log_output


def sample_output() -> str:
    record = "\x1e"
    first = (
        f"{record}abc123def456\x1f2026-09-20T10:00:00-05:00\x1fAda\n"
        "3\t1\tsrc/core.py"
    )
    second = (
        f"{record}def456789abc\x1f2026-09-21T11:30:00-05:00\x1fLinus\n"
        "2\t0\tsrc/core.py\n"
        "5\t5\tdocs/readme.md\n"
        "0\t0\tsrc/__init__.py"
    )
    return f"{first}\n{second}\n"


def test_parses_commit_headers():
    commits = parse_log_output(sample_output())

    assert len(commits) == 2
    assert commits[0].sha == "abc123def456"
    assert commits[0].author == "Ada"
    assert commits[0].date == datetime.fromisoformat("2026-09-20T10:00:00-05:00")


def test_parses_numstat_lines():
    commits = parse_log_output(sample_output())

    first_change = commits[0].files[0]
    assert first_change.path == "src/core.py"
    assert first_change.added == 3
    assert first_change.deleted == 1

    assert len(commits[1].files) == 3
    assert commits[1].files[2].path == "src/__init__.py"
    assert commits[1].files[2].added == 0


def test_paths_with_spaces_survive():
    output = "\x1esha\x1f2026-09-20T10:00:00-05:00\x1fAda\n1\t0\tdocs/user guide.md\n"
    commits = parse_log_output(output)

    assert commits[0].files[0].path == "docs/user guide.md"


def test_empty_history_parses_to_empty_list():
    assert parse_log_output("") == []


def test_trailing_whitespace_records_are_skipped():
    assert parse_log_output(sample_output() + "\n\n\n")[-1].sha == "def456789abc"


def test_collect_history_raises_on_non_repository(tmp_path):
    def fake_run(argv, **kwargs):
        class Proc:
            returncode = 128
            stderr = "fatal: not a git repository"

        return Proc()

    with pytest.raises(GitHistoryError, match="not a git repository"):
        collect_history(tmp_path, runner=fake_run)


def test_collect_history_wraps_missing_git_binary(tmp_path):
    def fake_run(argv, **kwargs):
        raise OSError("git: command not found")

    with pytest.raises(GitHistoryError, match="not available"):
        collect_history(tmp_path, runner=fake_run)


def test_argv_has_no_date_filtering_flags():
    from repoheat.gitlog import numstat_argv

    # date filtering happens in Python, not via git approxidate
    assert not any(arg.startswith("--since") for arg in numstat_argv(Path(".")))
