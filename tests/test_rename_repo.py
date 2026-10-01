"""Regression tests: rename detection and binary files, against a real repo.

Found when pointing repoheat at a repository that had moved files around
and contained images — the parser crashed on binary counts and attributed
renamed changes to paths that no longer exist.
"""

from repoheat.churn import aggregate
from repoheat.gitlog import collect_history
from repoheat.hotspots import bus_factor


def test_real_rename_is_resolved_to_the_new_path(make_repo_with_renames):
    repo = make_repo_with_renames()
    commits = collect_history(repo)

    newest = commits[0]
    # rename + modification reports as one entry on the NEW path with the
    # old->new diff counts; no ghost entry for the old path
    assert [(f.path, f.added, f.deleted) for f in newest.files] == [
        ("docs/notes.md", 2, 0)
    ]
    assert all(not f.binary for f in newest.files)


def test_real_binary_file_is_flagged(make_repo_with_renames):
    repo = make_repo_with_renames()
    commits = collect_history(repo)

    oldest = commits[1]
    logo = next(f for f in oldest.files if f.path == "logo.bin")
    assert logo.binary is True
    assert logo.added == 0 and logo.deleted == 0


def test_churn_lands_on_current_paths_only(make_repo_with_renames):
    repo = make_repo_with_renames()
    history = collect_history(repo)

    churn = aggregate(history)

    # no "{old => new}" ghosts; git attributes the original creation to the
    # old path and the rename+edit to the new one — per-path, like numstat
    notes = next(c for c in churn if c.path == "docs/notes.md")
    assert notes.commits == 1
    assert notes.added == 2 and notes.deleted == 0

    old = next(c for c in churn if c.path == "notes.md")
    assert old.commits == 1 and old.added == 1

    assert all("=>" not in c.path for c in churn)


def test_bus_factor_survives_renames_and_binaries(make_repo_with_renames):
    repo = make_repo_with_renames()
    history = collect_history(repo)

    rows = bus_factor(history)

    notes = next(r for r in rows if r.path == "docs/notes.md")
    assert notes.main_author == "Linus Torvalds"  # moved it

    old = next(r for r in rows if r.path == "notes.md")
    assert old.main_author == "Ada Lovelace"  # created it
